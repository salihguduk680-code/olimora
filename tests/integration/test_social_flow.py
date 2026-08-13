import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.core.database import async_session_factory
from app.main import app
from app.modules.astrology.infrastructure.models import UserModel

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_friend_request_message_and_read_flow() -> None:
    suffix = uuid.uuid4().hex
    credentials = [
        {"email": f"social-a-{suffix}@example.com", "password": "TestPass123!"},
        {"email": f"social-b-{suffix}@example.com", "password": "TestPass123!"},
    ]
    user_ids: list[uuid.UUID] = []

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            registrations = [
                await client.post("/api/v1/auth/register", json=item) for item in credentials
            ]
            assert [response.status_code for response in registrations] == [201, 201]

            user_ids = [uuid.UUID(response.json()["user"]["id"]) for response in registrations]
            tokens = [response.json()["access_token"] for response in registrations]
            headers = [{"Authorization": f"Bearer {token}"} for token in tokens]

            installation = await client.put(
                "/api/v1/notifications/installation",
                json={"fid": f"test-firebase-installation-{suffix}", "platform": "android"},
                headers=headers[1],
            )
            assert installation.status_code == 200
            assert installation.json()["fid"] == f"test-firebase-installation-{suffix}"

            overviews = [
                await client.get("/api/v1/social/overview", headers=item) for item in headers
            ]
            olimora_ids = [response.json()["me"]["olimora_id"] for response in overviews]

            request_response = await client.post(
                "/api/v1/social/friend-requests",
                json={"olimora_id": olimora_ids[1]},
                headers=headers[0],
            )
            assert request_response.status_code == 201
            request_id = request_response.json()["id"]

            incoming = await client.get("/api/v1/social/overview", headers=headers[1])
            assert incoming.status_code == 200
            assert len(incoming.json()["incoming"]) == 1

            accepted = await client.post(
                f"/api/v1/social/friend-requests/{request_id}/accept", headers=headers[1]
            )
            assert accepted.status_code == 204

            sent = await client.post(
                f"/api/v1/social/messages/{user_ids[1]}",
                json={"body": "Olimora sosyal akış testi"},
                headers=headers[0],
            )
            assert sent.status_code == 201
            assert sent.json()["is_mine"] is True

            unread = await client.get("/api/v1/social/overview", headers=headers[1])
            assert unread.status_code == 200
            assert unread.json()["total_unread"] == 1
            assert unread.json()["friends"][0]["unread_count"] == 1

            messages = await client.get(
                f"/api/v1/social/messages/{user_ids[0]}", headers=headers[1]
            )
            assert messages.status_code == 200
            assert messages.json()[0]["body"] == "Olimora sosyal akış testi"
            assert messages.json()[0]["is_mine"] is False

            sender_view = await client.get(
                f"/api/v1/social/messages/{user_ids[1]}", headers=headers[0]
            )
            assert sender_view.status_code == 200
            assert sender_view.json()[0]["read_at"] is not None

            read = await client.get("/api/v1/social/overview", headers=headers[1])
            assert read.status_code == 200
            assert read.json()["total_unread"] == 0
            assert read.json()["friends"][0]["unread_count"] == 0
    finally:
        if user_ids:
            async with async_session_factory() as session:
                await session.execute(delete(UserModel).where(UserModel.id.in_(user_ids)))
                await session.commit()
