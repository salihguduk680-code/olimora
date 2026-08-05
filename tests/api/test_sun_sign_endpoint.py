from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database_session
from app.main import app

client = TestClient(app)


def test_sun_sign_endpoint() -> None:
    response = client.post(
        "/api/v1/astrology/sun-sign",
        json={"birth_date": "1995-04-12"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "birth_date": "1995-04-12",
        "sign": "aries",
        "method": "conventional_tropical_date_range",
        "schema_version": "1.0",
        "requires_exact_calculation": False,
        "note": None,
    }


def test_sun_sign_endpoint_rejects_extra_fields() -> None:
    response = client.post(
        "/api/v1/astrology/sun-sign",
        json={"birth_date": "1995-04-12", "unknown": True},
    )

    assert response.status_code == 422


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "ok",
        "ephemeris": "ok",
        "app_version": "0.1.0",
        "wrapper_version": "2.10.3.6",
        "engine_version": "2.10.03",
        "tzdata_version": "2025.2",
    }


def test_health_endpoint_returns_503_when_database_is_unavailable() -> None:
    unavailable_session = AsyncMock(spec=AsyncSession)
    unavailable_session.execute.side_effect = SQLAlchemyError("database unavailable")

    async def override_database_session() -> AsyncIterator[AsyncSession]:
        yield unavailable_session

    app.dependency_overrides[get_database_session] = override_database_session
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_database_session, None)

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "DATABASE_UNAVAILABLE",
            "message": "Database health check failed.",
        }
    }
