import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.auth_dependencies import get_current_user
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def authenticated_user():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid.uuid4())
    yield
    app.dependency_overrides.clear()


def test_authenticated_chicago_landmark_preview() -> None:
    response = client.post(
        "/api/v1/astrology/natal-chart/preview",
        json={
            "local_datetime": "1990-07-15T14:30:00",
            "timezone_name": "America/Chicago",
            "latitude": 41.8796,
            "longitude": -87.6237,
            "place_name": "Art Institute of Chicago",
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["resolved_utc_datetime"] == "1990-07-15T19:30:00Z"
    assert result["engine_name"] == "Swiss Ephemeris"
    assert result["schema_version"] == "1.1"
    assert len(result["input_hash"]) == 64
    assert result["sun"]["sign"] == "cancer"
    assert result["moon"]["sign"] == "aries"
    assert result["ascendant"]["sign"] == "scorpio"
    assert result["sun"]["longitude"] == pytest.approx(113.0442710, abs=0.0001)
    assert [point["name"] for point in result["positions"]] == [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    assert len(result["houses"]) == 12
    assert result["houses"][0]["longitude"] == pytest.approx(result["ascendant"]["longitude"])
    assert all(1 <= point["house"] <= 12 for point in result["positions"])
    assert len(result["aspects"]) > 0


def test_invalid_coordinates_are_rejected() -> None:
    response = client.post(
        "/api/v1/astrology/natal-chart/preview",
        json={
            "local_datetime": "1990-07-15T14:30:00",
            "timezone_name": "Europe/Istanbul",
            "latitude": 100,
            "longitude": 39.269985,
            "place_name": "Invalid",
        },
    )

    assert response.status_code == 422


def test_preview_requires_authentication(authenticated_user) -> None:
    app.dependency_overrides.pop(get_current_user, None)
    response = client.post(
        "/api/v1/astrology/natal-chart/preview",
        json={
            "local_datetime": "1990-07-15T14:30:00",
            "timezone_name": "America/Chicago",
            "latitude": 41.8796,
            "longitude": -87.6237,
            "place_name": "Art Institute of Chicago",
        },
    )
    assert response.status_code == 401
