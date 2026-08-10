import asyncio
import json
from functools import lru_cache

import firebase_admin  # type: ignore[import-untyped]
from firebase_admin import credentials, messaging

from app.core.config import get_settings


class FirebasePushService:
    def __init__(self) -> None:
        settings = get_settings()
        self._app: firebase_admin.App | None = None
        if not settings.firebase_project_id or not settings.firebase_service_account_json:
            return
        service_account = json.loads(settings.firebase_service_account_json)
        credential = credentials.Certificate(service_account)
        try:
            self._app = firebase_admin.initialize_app(
                credential,
                options={"projectId": settings.firebase_project_id},
                name="olimora-push",
            )
        except ValueError:
            self._app = firebase_admin.get_app("olimora-push")

    @property
    def enabled(self) -> bool:
        return self._app is not None

    async def send_new_message(self, *, fids: list[str], sender_name: str) -> None:
        if self._app is None or not fids:
            return
        messages = [
            messaging.Message(
                notification=messaging.Notification(
                    title=f"{sender_name} sana yazdı",
                    body="Olimora'da yeni bir mesajın var.",
                ),
                data={"type": "direct_message"},
                fid=fid,
            )
            for fid in fids
        ]
        await asyncio.to_thread(messaging.send_each, messages, app=self._app)


@lru_cache
def get_firebase_push_service() -> FirebasePushService:
    return FirebasePushService()
