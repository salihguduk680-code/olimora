from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.modules.astrology.domain.exceptions import (
    EphemerisCalculationError,
    EphemerisConfigurationError,
)
from app.modules.astrology.infrastructure.swisseph_calculator import (
    SwissEphemerisCalculator,
    calculator,
)


def test_missing_ephemeris_directory_is_rejected() -> None:
    missing_path = Path(__file__).parent / "does-not-exist"

    with pytest.raises(EphemerisConfigurationError, match="files are missing"):
        SwissEphemerisCalculator(missing_path)


def test_placidus_unavailable_at_polar_latitude_is_controlled() -> None:
    with pytest.raises(EphemerisCalculationError, match="House calculation is unavailable"):
        calculator.calculate_preview(
            utc_datetime=datetime(2002, 3, 12, 18, tzinfo=UTC),
            latitude=89.0,
            longitude=39.269985,
            house_system="P",
        )


def test_calculation_config_preserves_hash_metadata_contract() -> None:
    config = calculator.get_calculation_config(house_system="P")

    assert config.calculator_name == "Swiss Ephemeris"
    assert config.engine_version == "2.10.03"
    assert config.wrapper_name == "pysweph"
    assert config.wrapper_version == "pysweph-2.10.3.6"
    assert config.house_placement_method == "ecliptic_longitude_cusp_interval"
    assert config.zodiac_type == "tropical"
    assert config.calculation_flags == 258
    assert len(config.requested_bodies) == 10


def test_calculation_returns_julian_day_ut() -> None:
    chart = calculator.calculate_natal_chart(
        utc_datetime=datetime(2002, 3, 12, 18, tzinfo=UTC),
        latitude=41.047615,
        longitude=39.269985,
        house_system="P",
    )

    assert chart.julian_day_ut == pytest.approx(2452346.25)
