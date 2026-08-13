import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FriendRequestCreate(BaseModel):
    olimora_id: str = Field(min_length=20, max_length=21, pattern=r"^oli_[a-f0-9]{16}$")

    @field_validator("olimora_id", mode="before")
    @classmethod
    def normalize_olimora_id(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower().removeprefix("@")
        return value


class SocialUserResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    olimora_id: str
    unread_count: int = 0
    is_online: bool = False
    last_seen_at: datetime | None = None
    status_message: str | None = None


class StatusUpdate(BaseModel):
    status_message: str | None = Field(default=None, max_length=60)

    @field_validator("status_message")
    @classmethod
    def clean_status(cls, value: str | None) -> str | None:
        cleaned = value.strip() if value else ""
        return cleaned or None


class FriendRequestResponse(BaseModel):
    id: uuid.UUID
    user: SocialUserResponse
    created_at: datetime


class SocialOverviewResponse(BaseModel):
    me: SocialUserResponse
    friends: list[SocialUserResponse]
    incoming: list[FriendRequestResponse]
    outgoing: list[FriendRequestResponse]
    total_unread: int = 0


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def clean_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("mesaj boş olamaz")
        return cleaned


class MessageResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    created_at: datetime
    read_at: datetime | None = None
    is_mine: bool
