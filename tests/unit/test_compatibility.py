from app.api.v1.endpoints.compatibility import _aspect_between, _bounded, _positions


def test_cross_chart_aspects_use_shortest_zodiac_distance() -> None:
    assert _aspect_between(358.0, 2.0) == ("conjunction", 4.0, 8)
    assert _aspect_between(10.0, 130.0) == ("trine", 0.0, 7)
    assert _aspect_between(10.0, 100.0) == ("square", 0.0, -6)


def test_positions_ignore_malformed_chart_items() -> None:
    result: dict[str, object] = {
        "positions": [
            {"name": "Sun", "longitude": 351.2},
            {"name": "Moon", "longitude": "invalid"},
            "invalid",
        ]
    }
    assert _positions(result) == [{"name": "sun", "longitude": 351.2}]


def test_scores_are_bounded_to_non_absolute_language() -> None:
    assert _bounded(-50) == 15
    assert _bounded(200) == 95
