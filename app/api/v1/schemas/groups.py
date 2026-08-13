import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.api.v1.schemas.social import SocialUserResponse


class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    member_ids: list[uuid.UUID] = Field(default_factory=list, max_length=19)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("grup adı çok kısa")
        return cleaned

    @field_validator("member_ids")
    @classmethod
    def unique_members(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(set(value)) != len(value):
            raise ValueError("aynı üye birden fazla eklenemez")
        return value


class GroupMemberResponse(BaseModel):
    user: SocialUserResponse
    role: str


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    members: list[GroupMemberResponse]
    unread_count: int = 0
    created_at: datetime


class GroupMessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def clean_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("mesaj boş olamaz")
        return cleaned


class GroupMessageResponse(BaseModel):
    id: uuid.UUID
    sender: SocialUserResponse
    body: str
    created_at: datetime
    is_mine: bool
