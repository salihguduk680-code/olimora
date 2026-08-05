from app.modules.astrology.domain.aspects import angular_separation, calculate_aspects
from app.modules.astrology.domain.natal_chart import ChartPoint


def _point(name: str, longitude: float) -> ChartPoint:
    return ChartPoint(
        name=name,
        longitude=longitude,
        sign="test",
        degree_in_sign=longitude % 30.0,
        speed_longitude=1.0,
        is_retrograde=False,
        house=1,
    )


def test_angular_separation_handles_zero_degree_wrap() -> None:
    assert angular_separation(359.0, 1.0) == 2.0


def test_exact_major_aspects_are_detected() -> None:
    positions = (
        _point("a", 0.0),
        _point("b", 60.0),
        _point("c", 90.0),
        _point("d", 120.0),
        _point("e", 180.0),
    )
    aspects = calculate_aspects(positions)
    types_from_a = {aspect.aspect_type for aspect in aspects if aspect.body_a == "a"}
    assert types_from_a == {"sextile", "square", "trine", "opposition"}


def test_aspect_outside_orb_is_not_returned() -> None:
    aspects = calculate_aspects((_point("a", 0.0), _point("b", 65.0)))
    assert aspects == ()
