import pytest

from app.modules.astrology.domain.exceptions import EphemerisCalculationError
from app.modules.astrology.infrastructure.swisseph_calculator import (
    _house_for_longitude,
    _normalize_cusps,
)


def test_normalize_thirteen_cusps_removes_empty_index_zero() -> None:
    expected = tuple(float(value) for value in range(0, 360, 30))
    assert _normalize_cusps((0.0, *expected)) == expected


def test_unexpected_cusp_count_is_rejected() -> None:
    with pytest.raises(EphemerisCalculationError):
        _normalize_cusps((0.0, 30.0))


def test_house_placement_handles_360_degree_wrap() -> None:
    cusps = tuple(float((15 + value) % 360) for value in range(0, 360, 30))
    assert _house_for_longitude(350.0, cusps) == 12
    assert _house_for_longitude(5.0, cusps) == 12
    assert _house_for_longitude(15.0, cusps) == 1
