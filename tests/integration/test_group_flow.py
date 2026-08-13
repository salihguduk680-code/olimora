import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.core.database import async_session_factory
from app.main import app
from app.modules.astrology.infrastructure.models import UserModel

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_group_membership_message_and_access_control() -> None:
    suffix = uuid.uuid4().hex
    credentials = [
        {"email": f"group-{index}-{suffix}@example.com", "password": "TestPass123!"}
        for index in range(3)
    ]
    user_ids: list[uuid.UUID] = []

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            registrations = [
                await client.post("/api/v1/auth/register", json=item) for item in credentials
            ]
            assert [response.status_code for response in registrations] == [201, 201, 201]
            user_ids = [uuid.UUID(response.json()["user"]["id"]) for response in registrations]
            headers = [
                {"Authorization": f"Bearer {response.json()['access_token']}"}
                for response in registrations
            ]
            overviews = [
                await client.get("/api/v1/social/overview", headers=item) for item in headers
            ]

            friend_request = await client.post(
                "/api/v1/social/friend-requests",
                json={"olimora_id": overviews[1].json()["me"]["olimora_id"]},
                headers=headers[0],
            )
            assert friend_request.status_code == 201
            accepted = await client.post(
                f"/api/v1/social/friend-requests/{friend_request.json()['id']}/accept",
                headers=headers[1],
            )
            assert accepted.status_code == 204

            created = await client.post(
                "/api/v1/social/groups",
                json={"name": "Gökyüzü Ekibi", "member_ids": [str(user_ids[1])]},
                headers=headers[0],
            )
            assert created.status_code == 201
            group_id = created.json()["id"]
            assert len(created.json()["members"]) == 2

            sent = await client.post(
                f"/api/v1/social/groups/{group_id}/messages",
                json={"body": "İlk grup mesajı"},
                headers=headers[1],
            )
            assert sent.status_code == 201
            assert sent.json()["is_mine"] is True

            owner_groups = await client.get("/api/v1/social/groups", headers=headers[0])
            assert owner_groups.status_code == 200
            assert owner_groups.json()[0]["unread_count"] == 1

            messages = await client.get(
                f"/api/v1/social/groups/{group_id}/messages", headers=headers[0]
            )
            assert messages.status_code == 200
            assert messages.json()[0]["body"] == "İlk grup mesajı"

            denied = await client.get(
                f"/api/v1/social/groups/{group_id}/messages", headers=headers[2]
            )
            assert denied.status_code == 404
    finally:
        if user_ids:
            async with async_session_factory() as session:
                await session.execute(delete(UserModel).where(UserModel.id.in_(user_ids)))
                await session.commit()
