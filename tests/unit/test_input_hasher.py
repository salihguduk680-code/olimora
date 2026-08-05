from datetime import UTC, datetime

from app.modules.astrology.application.input_hasher import create_natal_chart_input_hash


def _hash(**overrides: object) -> str:
    arguments: dict[str, object] = {
        "resolved_utc_datetime": datetime(2002, 3, 12, 18, tzinfo=UTC),
        "latitude": 41.047615,
        "longitude": 39.269985,
        "house_system": "P",
        "requested_bodies": ("sun", "moon", "mercury"),
        "calculator_name": "Swiss Ephemeris",
        "engine_version": "2.10.03",
        "wrapper_version": "pysweph-2.10.3.6",
        "calculation_flags": 258,
    }
    arguments.update(overrides)
    return create_natal_chart_input_hash(**arguments)  # type: ignore[arg-type]


def test_same_input_produces_same_hash() -> None:
    assert _hash() == _hash()


def test_requested_body_order_does_not_change_hash() -> None:
    assert _hash(requested_bodies=("sun", "moon", "mercury")) == _hash(
        requested_bodies=("mercury", "sun", "moon")
    )


def test_time_coordinate_and_engine_changes_change_hash() -> None:
    original = _hash()
    assert _hash(resolved_utc_datetime=datetime(2002, 3, 12, 19, tzinfo=UTC)) != original
    assert _hash(latitude=41.047616) != original
    assert _hash(house_system="W") != original
    assert _hash(engine_version="2.10.04") != original


def test_equivalent_decimal_coordinates_produce_same_hash() -> None:
    assert _hash(latitude=41.0) == _hash(latitude=41.0000)
