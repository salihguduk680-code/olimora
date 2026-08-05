from datetime import date

import pytest

from app.modules.astrology.domain.enums import ZodiacSign
from app.modules.astrology.domain.sun_sign import calculate_conventional_sun_sign


@pytest.mark.parametrize(
    ("birth_date", "expected"),
    [
        (date(1995, 1, 1), ZodiacSign.CAPRICORN),
        (date(1995, 1, 20), ZodiacSign.AQUARIUS),
        (date(2000, 2, 29), ZodiacSign.PISCES),
        (date(1995, 3, 21), ZodiacSign.ARIES),
        (date(1995, 4, 20), ZodiacSign.TAURUS),
        (date(1995, 5, 21), ZodiacSign.GEMINI),
        (date(1995, 6, 21), ZodiacSign.CANCER),
        (date(1995, 7, 23), ZodiacSign.LEO),
        (date(1995, 8, 23), ZodiacSign.VIRGO),
        (date(1995, 9, 23), ZodiacSign.LIBRA),
        (date(1995, 10, 23), ZodiacSign.SCORPIO),
        (date(1995, 11, 22), ZodiacSign.SAGITTARIUS),
        (date(1995, 12, 22), ZodiacSign.CAPRICORN),
    ],
)
def test_calculates_conventional_sign(birth_date: date, expected: ZodiacSign) -> None:
    result = calculate_conventional_sun_sign(birth_date)

    assert result.sign is expected


def test_marks_ingress_boundary_for_exact_calculation() -> None:
    result = calculate_conventional_sun_sign(date(1995, 4, 20))

    assert result.requires_exact_calculation is True
    assert result.note is not None


def test_regular_date_does_not_require_exact_calculation() -> None:
    result = calculate_conventional_sun_sign(date(1995, 4, 12))

    assert result.sign is ZodiacSign.ARIES
    assert result.requires_exact_calculation is False
    assert result.note is None
