from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PlanetPosition:
    name: str
    longitude: float
    sign: str
    degree_in_sign: float
    speed_longitude: float | None
    is_retrograde: bool | None
    house: int | None
    latitude: float | None = None
    distance: float | None = None


ChartPoint = PlanetPosition


@dataclass(frozen=True, slots=True)
class HouseCusp:
    house_number: int
    longitude: float
    sign: str
    degree_in_sign: float


@dataclass(frozen=True, slots=True)
class Aspect:
    body_a: str
    body_b: str
    aspect_type: str
    exact_angle: float
    actual_angle: float
    orb: float


@dataclass(frozen=True, slots=True)
class CalculationConfig:
    calculator_name: str
    engine_version: str
    wrapper_name: str
    wrapper_version: str
    house_system: str
    house_placement_method: str
    zodiac_type: str
    calculation_flags: int
    requested_bodies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EngineMetadata:
    name: str
    engine_version: str
    wrapper_name: str
    wrapper_version: str
    house_system: str
    house_placement_method: str
    zodiac_type: str
    calculation_flags: int


@dataclass(frozen=True, slots=True)
class NatalChartPreview:
    utc_datetime: datetime
    julian_day_ut: float
    latitude: float
    longitude: float
    house_system: str
    engine: EngineMetadata
    sun: ChartPoint
    moon: ChartPoint
    ascendant: ChartPoint
    positions: tuple[ChartPoint, ...]
    houses: tuple[HouseCusp, ...]
    aspects: tuple[Aspect, ...]

    @property
    def engine_name(self) -> str:
        return self.engine.name

    @property
    def engine_version(self) -> str:
        return self.engine.engine_version

    @property
    def calculation_flags(self) -> int:
        return self.engine.calculation_flags
