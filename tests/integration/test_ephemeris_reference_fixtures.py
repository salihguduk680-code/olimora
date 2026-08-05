import json
from datetime import datetime
from pathlib import Path

import pytest

from app.modules.astrology.infrastructure.swisseph_calculator import calculator

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "natal_chart_reference_cases.json"


@pytest.mark.integration
@pytest.mark.parametrize("case", json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))
def test_ephemeris_reference_case(case: dict[str, object]) -> None:
    chart = calculator.calculate_natal_chart(
        utc_datetime=datetime.fromisoformat(str(case["utc_datetime"])),
        latitude=float(case["latitude"]),
        longitude=float(case["longitude"]),
        house_system=str(case["house_system"]),
    )
    expected_positions = case["expected_positions"]
    assert isinstance(expected_positions, dict)
    actual_positions = {position.name: position for position in chart.positions}

    assert chart.julian_day_ut == pytest.approx(float(case["expected_julian_day_ut"]))
    assert chart.ascendant.longitude == pytest.approx(
        float(case["expected_ascendant"]), abs=float(case["cusp_tolerance"])
    )
    for name, raw_expected in expected_positions.items():
        assert isinstance(raw_expected, dict)
        expected = raw_expected
        actual = actual_positions[name]
        assert actual.longitude == pytest.approx(
            float(expected["longitude"]), abs=float(case["longitude_tolerance"])
        )
        assert actual.speed_longitude == pytest.approx(
            float(expected["speed_longitude"]), abs=float(case["speed_tolerance"])
        )
        assert actual.is_retrograde is (float(expected["speed_longitude"]) < 0.0)

    expected_cusps = case["expected_cusps"]
    assert isinstance(expected_cusps, list)
    assert [house.longitude for house in chart.houses] == pytest.approx(
        [float(value) for value in expected_cusps], abs=float(case["cusp_tolerance"])
    )
