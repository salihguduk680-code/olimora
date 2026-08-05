from dataclasses import dataclass
from datetime import date

from app.modules.astrology.domain.enums import ZodiacSign

SCHEMA_VERSION = "1.0"
METHOD = "conventional_tropical_date_range"


@dataclass(frozen=True, slots=True)
class SunSignResult:
    sign: ZodiacSign
    method: str
    schema_version: str
    requires_exact_calculation: bool
    note: str | None


_STARTS: tuple[tuple[tuple[int, int], ZodiacSign], ...] = (
    ((1, 20), ZodiacSign.AQUARIUS),
    ((2, 19), ZodiacSign.PISCES),
    ((3, 21), ZodiacSign.ARIES),
    ((4, 20), ZodiacSign.TAURUS),
    ((5, 21), ZodiacSign.GEMINI),
    ((6, 21), ZodiacSign.CANCER),
    ((7, 23), ZodiacSign.LEO),
    ((8, 23), ZodiacSign.VIRGO),
    ((9, 23), ZodiacSign.LIBRA),
    ((10, 23), ZodiacSign.SCORPIO),
    ((11, 22), ZodiacSign.SAGITTARIUS),
    ((12, 22), ZodiacSign.CAPRICORN),
)

_BOUNDARY_DATES = frozenset(
    (month, day) for (month, start_day), _sign in _STARTS for day in (start_day - 1, start_day)
)


def calculate_conventional_sun_sign(birth_date: date) -> SunSignResult:
    """Return the conventional tropical Sun sign for a calendar date.

    This deliberately does not claim astronomical precision. On ingress boundary
    dates, birth time and place are required for the exact solar longitude.
    """
    month_day = (birth_date.month, birth_date.day)
    sign = ZodiacSign.CAPRICORN

    for start, candidate in _STARTS:
        if month_day >= start:
            sign = candidate
        else:
            break

    is_boundary = month_day in _BOUNDARY_DATES
    note = None
    if is_boundary:
        note = (
            "Bu tarih burç geçiş sınırına yakındır. Kesin sonuç için doğum saati, "
            "doğum yeri ve astronomik efemeris hesabı gerekir."
        )

    return SunSignResult(
        sign=sign,
        method=METHOD,
        schema_version=SCHEMA_VERSION,
        requires_exact_calculation=is_boundary,
        note=note,
    )
