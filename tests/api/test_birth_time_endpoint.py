from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_resolve_chicago_summer_time() -> None:
    response = client.post(
        "/api/v1/astrology/birth-time/resolve",
        json={
            "local_datetime": "1990-07-15T14:30:00",
            "timezone_name": "America/Chicago",
        },
    )

    assert response.status_code == 200
    assert response.json()["resolved_utc_datetime"] == "1990-07-15T19:30:00Z"
    assert response.json()["utc_offset_minutes"] == -300


def test_ambiguous_birth_time_returns_choices() -> None:
    response = client.post(
        "/api/v1/astrology/birth-time/resolve",
        json={
            "local_datetime": "2023-10-29T02:30:00",
            "timezone_name": "Europe/Berlin",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "AMBIGUOUS_LOCAL_TIME"
    assert set(response.json()["detail"]["valid_offsets"]) == {60, 120}


def test_nonexistent_birth_time_returns_clear_error() -> None:
    response = client.post(
        "/api/v1/astrology/birth-time/resolve",
        json={
            "local_datetime": "2023-03-26T02:30:00",
            "timezone_name": "Europe/Berlin",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "NONEXISTENT_LOCAL_TIME"


def test_aware_local_datetime_is_rejected() -> None:
    response = client.post(
        "/api/v1/astrology/birth-time/resolve",
        json={
            "local_datetime": "1990-07-15T14:30:00-05:00",
            "timezone_name": "America/Chicago",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_INPUT"
