import importlib.metadata
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

import swisseph as swe  # type: ignore[import-not-found]

from app.modules.astrology.domain.aspects import calculate_aspects
from app.modules.astrology.domain.exceptions import (
    EphemerisCalculationError,
    EphemerisConfigurationError,
)
from app.modules.astrology.domain.natal_chart import (
    CalculationConfig,
    ChartPoint,
    EngineMetadata,
    HouseCusp,
    NatalChartPreview,
)

SIGNS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

PLANETS = (
    ("sun", swe.SUN),
    ("moon", swe.MOON),
    ("mercury", swe.MERCURY),
    ("venus", swe.VENUS),
    ("mars", swe.MARS),
    ("jupiter", swe.JUPITER),
    ("saturn", swe.SATURN),
    ("uranus", swe.URANUS),
    ("neptune", swe.NEPTUNE),
    ("pluto", swe.PLUTO),
)
ENGINE_VERSION = str(swe.version)
CALCULATION_FLAGS = int(swe.FLG_SWIEPH | swe.FLG_SPEED)
WRAPPER_VERSION = importlib.metadata.version("pysweph")


def _chart_point(
    *,
    name: str,
    longitude: float,
    latitude: float | None = None,
    distance: float | None = None,
    speed_longitude: float | None = None,
    house: int | None = None,
) -> ChartPoint:
    normalized = longitude % 360.0
    sign_index = int(normalized // 30.0)
    return ChartPoint(
        name=name,
        longitude=normalized,
        latitude=latitude,
        distance=distance,
        sign=SIGNS[sign_index],
        degree_in_sign=normalized % 30.0,
        speed_longitude=speed_longitude,
        is_retrograde=None if speed_longitude is None else speed_longitude < 0.0,
        house=house,
    )


def _normalize_cusps(raw_cusps: tuple[float, ...]) -> tuple[float, ...]:
    if len(raw_cusps) == 12:
        selected = raw_cusps
    elif len(raw_cusps) == 13:
        selected = raw_cusps[1:]
    else:
        raise EphemerisCalculationError("Swiss Ephemeris returned an unexpected cusp count.")
    return tuple(value % 360.0 for value in selected)


def _house_for_longitude(longitude: float, cusps: tuple[float, ...]) -> int:
    normalized = longitude % 360.0
    for index, start in enumerate(cusps):
        end = cusps[(index + 1) % 12]
        if (normalized - start) % 360.0 < (end - start) % 360.0:
            return index + 1
    raise EphemerisCalculationError("Planet could not be assigned to a house.")


class SwissEphemerisCalculator:
    def __init__(self, ephemeris_path: Path) -> None:
        required_files = ("sepl_18.se1", "semo_18.se1")
        missing = [name for name in required_files if not (ephemeris_path / name).is_file()]
        if missing:
            raise EphemerisConfigurationError("Required Swiss Ephemeris files are missing.")
        self._ephemeris_path = ephemeris_path
        self._lock = RLock()
        swe.set_ephe_path(str(ephemeris_path))

    @property
    def requested_bodies(self) -> tuple[str, ...]:
        return tuple(name for name, _ in PLANETS)

    @property
    def engine_version(self) -> str:
        return ENGINE_VERSION

    @property
    def calculation_flags(self) -> int:
        return CALCULATION_FLAGS

    @property
    def wrapper_version(self) -> str:
        return WRAPPER_VERSION

    def get_calculation_config(self, *, house_system: str) -> CalculationConfig:
        if house_system != "P":
            raise EphemerisCalculationError("Only Placidus house system is supported.")
        return CalculationConfig(
            calculator_name="Swiss Ephemeris",
            engine_version=self.engine_version,
            wrapper_name="pysweph",
            wrapper_version=f"pysweph-{self.wrapper_version}",
            house_system=house_system,
            house_placement_method="ecliptic_longitude_cusp_interval",
            zodiac_type="tropical",
            calculation_flags=self.calculation_flags,
            requested_bodies=self.requested_bodies,
        )

    def _planet(self, *, julian_day: float, body: int, name: str) -> tuple[ChartPoint, int]:
        values, returned_flags, error_message = swe.calc_ut(
            julian_day, body, swe.FLG_SWIEPH | swe.FLG_SPEED
        )
        if error_message or not returned_flags & swe.FLG_SWIEPH:
            raise EphemerisCalculationError(
                "Swiss Ephemeris calculation was unavailable; fallback was rejected."
            )
        if not returned_flags & swe.FLG_SPEED:
            raise EphemerisCalculationError("Swiss Ephemeris did not return speed data.")
        return (
            _chart_point(
                name=name,
                longitude=values[0],
                latitude=values[1],
                distance=values[2],
                speed_longitude=values[3],
            ),
            returned_flags,
        )

    def calculate_natal_chart(
        self,
        *,
        utc_datetime: datetime,
        latitude: float,
        longitude: float,
        house_system: str = "P",
    ) -> NatalChartPreview:
        if utc_datetime.tzinfo is None or utc_datetime.utcoffset() != UTC.utcoffset(utc_datetime):
            raise EphemerisCalculationError("utc_datetime must be timezone-aware UTC.")
        if house_system != "P":
            raise EphemerisCalculationError("Only Placidus house system is supported.")

        utc_datetime = utc_datetime.astimezone(UTC)
        decimal_hour = (
            utc_datetime.hour
            + utc_datetime.minute / 60.0
            + utc_datetime.second / 3600.0
            + utc_datetime.microsecond / 3_600_000_000.0
        )
        julian_day = swe.julday(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            decimal_hour,
            swe.GREG_CAL,
        )
        # Swiss Ephemeris keeps process/thread-level state. The singleton adapter
        # serializes access and reapplies the one configured path in worker threads.
        with self._lock:
            swe.set_ephe_path(str(self._ephemeris_path))
            try:
                raw_cusps, angles = swe.houses_ex(
                    julian_day, latitude, longitude, house_system.encode("ascii"), 0
                )
            except swe.Error as error:
                raise EphemerisCalculationError("House calculation is unavailable.") from error

            cusps = _normalize_cusps(raw_cusps)
            calculated: list[tuple[ChartPoint, int]] = []
            for name, body in PLANETS:
                point, returned_flags = self._planet(julian_day=julian_day, body=body, name=name)
                calculated.append(
                    (
                        _chart_point(
                            name=point.name,
                            longitude=point.longitude,
                            latitude=point.latitude,
                            distance=point.distance,
                            speed_longitude=point.speed_longitude,
                            house=_house_for_longitude(point.longitude, cusps),
                        ),
                        returned_flags,
                    )
                )

        positions = tuple(point for point, _ in calculated)
        calculation_flags = 0
        for _, returned_flags in calculated:
            calculation_flags |= returned_flags
        houses = tuple(
            HouseCusp(
                house_number=index + 1,
                longitude=cusp,
                sign=SIGNS[int(cusp // 30.0)],
                degree_in_sign=cusp % 30.0,
            )
            for index, cusp in enumerate(cusps)
        )

        return NatalChartPreview(
            utc_datetime=utc_datetime,
            julian_day_ut=julian_day,
            latitude=latitude,
            longitude=longitude,
            house_system=house_system,
            engine=EngineMetadata(
                name="Swiss Ephemeris",
                engine_version=swe.version,
                wrapper_name="pysweph",
                wrapper_version=self.wrapper_version,
                house_system=house_system,
                house_placement_method="ecliptic_longitude_cusp_interval",
                zodiac_type="tropical",
                calculation_flags=calculation_flags,
            ),
            sun=positions[0],
            moon=positions[1],
            ascendant=_chart_point(name="ascendant", longitude=angles[0]),
            positions=positions,
            houses=houses,
            aspects=calculate_aspects(positions),
        )

    def calculate_preview(
        self,
        *,
        utc_datetime: datetime,
        latitude: float,
        longitude: float,
        house_system: str = "P",
    ) -> NatalChartPreview:
        """Backward-compatible alias for the Sprint 1 preview endpoint."""
        return self.calculate_natal_chart(
            utc_datetime=utc_datetime,
            latitude=latitude,
            longitude=longitude,
            house_system=house_system,
        )


DEFAULT_EPHEMERIS_PATH = Path(__file__).resolve().parents[4] / "ephe"
calculator = SwissEphemerisCalculator(DEFAULT_EPHEMERIS_PATH)
