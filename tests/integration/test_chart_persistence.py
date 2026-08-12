import asyncio
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, text

from app.core.database import async_session_factory
from app.main import app
from app.modules.astrology.infrastructure.models import NatalChartModel

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def _create_profile(client: AsyncClient) -> tuple[str, dict[str, str]]:
    suffix = uuid.uuid4().hex
    unique_name = f"Concurrency Test {suffix}"
    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": f"chart-{suffix}@example.com", "password": "TestPass123!"},
    )
    assert registration.status_code == 201
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    response = await client.post(
        "/api/v1/birth-profiles",
        json={
            "name": unique_name,
            "local_datetime": "1990-07-15T14:30:00",
            "timezone_name": "America/Chicago",
            "latitude": 41.8796,
            "longitude": -87.6237,
            "place_name": "Art Institute of Chicago",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return str(response.json()["id"]), headers


async def test_repeated_chart_request_is_cached() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        profile_id, headers = await _create_profile(client)
        first = await client.post(
            f"/api/v1/birth-profiles/{profile_id}/natal-chart",
            json={"house_system": "P"},
            headers=headers,
        )
        second = await client.post(
            f"/api/v1/birth-profiles/{profile_id}/natal-chart",
            json={"house_system": "P"},
            headers=headers,
        )

    assert first.status_code == 201
    assert first.json()["status"] == "calculated"
    assert second.status_code == 200
    assert second.json()["status"] == "cached"
    assert first.json()["chart_id"] == second.json()["chart_id"]


async def test_fifty_concurrent_requests_create_one_chart_row() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        profile_id, headers = await _create_profile(client)
        responses = await asyncio.gather(
            *(
                client.post(
                    f"/api/v1/birth-profiles/{profile_id}/natal-chart",
                    json={"house_system": "P"},
                    headers=headers,
                )
                for _ in range(50)
            )
        )

    assert sum(response.status_code == 201 for response in responses) == 1
    assert sum(response.status_code == 200 for response in responses) == 49
    assert len({response.json()["chart_id"] for response in responses}) == 1

    async with async_session_factory() as session:
        count = await session.scalar(
            select(func.count(NatalChartModel.id)).where(
                NatalChartModel.birth_profile_id == uuid.UUID(profile_id)
            )
        )
    assert count == 1


async def test_unknown_birth_profile_returns_404() -> None:
    missing_profile_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        suffix = uuid.uuid4().hex
        registration = await client.post(
            "/api/v1/auth/register",
            json={"email": f"missing-{suffix}@example.com", "password": "TestPass123!"},
        )
        headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
        response = await client.post(
            f"/api/v1/birth-profiles/{missing_profile_id}/natal-chart",
            json={"house_system": "P"},
            headers=headers,
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Birth profile not found."}


async def test_database_schema_has_required_postgresql_contracts() -> None:
    async with async_session_factory() as session:
        result_json_type = await session.scalar(
            text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = 'natal_charts' "
                "AND column_name = 'result_json'"
            )
        )
        timestamp_types = set(
            (
                await session.execute(
                    text(
                        "SELECT table_name, column_name, data_type "
                        "FROM information_schema.columns "
                        "WHERE table_schema = 'public' AND ("
                        "(table_name = 'birth_profiles' AND column_name IN "
                        "('resolved_utc_datetime', 'created_at', 'updated_at')) OR "
                        "(table_name = 'natal_charts' AND column_name = 'calculated_at'))"
                    )
                )
            ).tuples()
        )
        constraints = set(
            (
                await session.execute(
                    text(
                        "SELECT conname FROM pg_constraint "
                        "WHERE conrelid IN ('birth_profiles'::regclass, 'natal_charts'::regclass)"
                    )
                )
            ).scalars()
        )
        indexes = set(
            (
                await session.execute(
                    text("SELECT indexname FROM pg_indexes WHERE tablename = 'natal_charts'")
                )
            ).scalars()
        )
        cascade_code = await session.scalar(
            text(
                "SELECT confdeltype FROM pg_constraint "
                "WHERE conname = 'natal_charts_birth_profile_id_fkey'"
            )
        )

    assert result_json_type == "jsonb"
    assert len(timestamp_types) == 4
    assert all(data_type == "timestamp with time zone" for _, _, data_type in timestamp_types)
    assert "uq_natal_chart_profile_input_hash" in constraints
    assert "ck_birth_profile_latitude" in constraints
    assert "ck_birth_profile_longitude" in constraints
    assert "ck_birth_profile_name_not_blank" in constraints
    assert "ix_natal_charts_birth_profile_id" in indexes
    assert cascade_code == b"c"
