import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FriendRequestCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)


class SocialUserResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    email: str


class FriendRequestResponse(BaseModel):
    id: uuid.UUID
    user: SocialUserResponse
    created_at: datetime


class SocialOverviewResponse(BaseModel):
    friends: list[SocialUserResponse]
    incoming: list[FriendRequestResponse]
    outgoing: list[FriendRequestResponse]


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    created_at: datetime
    is_mine: bool
