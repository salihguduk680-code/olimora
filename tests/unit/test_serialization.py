from datetime import UTC, datetime

from app.modules.astrology.application.serialization import serialize_calculation
from app.modules.astrology.infrastructure.swisseph_calculator import calculator


def test_slots_domain_chart_serializes_explicitly() -> None:
    chart = calculator.calculate_natal_chart(
        utc_datetime=datetime(1990, 7, 15, 19, 30, tzinfo=UTC),
        latitude=41.8796,
        longitude=-87.6237,
        house_system="P",
    )

    result = serialize_calculation(chart)
    positions = result["positions"]
    engine = result["engine"]

    assert isinstance(positions, list)
    assert isinstance(engine, dict)
    assert result["schema_version"] == "1.1"
    assert result["utc_datetime"] == "1990-07-15T19:30:00.000000Z"
    assert engine["name"] == "Swiss Ephemeris"
    assert engine["wrapper_version"] == "2.10.3.6"
    assert positions[0]["name"] == "sun"
    assert isinstance(positions[0]["latitude"], float)
    assert isinstance(positions[0]["distance"], float)


def test_ascendant_has_no_planet_distance_or_speed() -> None:
    chart = calculator.calculate_natal_chart(
        utc_datetime=datetime(1990, 7, 15, 19, 30, tzinfo=UTC),
        latitude=41.8796,
        longitude=-87.6237,
        house_system="P",
    )
    ascendant = serialize_calculation(chart)["ascendant"]

    assert isinstance(ascendant, dict)
    assert ascendant["latitude"] is None
    assert ascendant["distance"] is None
    assert ascendant["speed_longitude"] is None
    assert ascendant["is_retrograde"] is None
