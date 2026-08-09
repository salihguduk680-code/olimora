import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.schemas.social import (
    FriendRequestCreate,
    FriendRequestResponse,
    MessageCreate,
    MessageResponse,
    SocialOverviewResponse,
    SocialUserResponse,
)
from app.core.database import get_database_session
from app.modules.astrology.infrastructure.models import (
    BirthProfileModel,
    DirectMessageModel,
    FriendshipModel,
    UserModel,
)

router = APIRouter(prefix="/social")


@router.get("/overview", response_model=SocialOverviewResponse)
async def social_overview(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> SocialOverviewResponse:
    relationships = (
        await session.execute(
            select(FriendshipModel)
            .where(
                or_(
                    FriendshipModel.user_low_id == user.id,
                    FriendshipModel.user_high_id == user.id,
                )
            )
            .order_by(FriendshipModel.created_at.desc())
        )
    ).scalars()
    friends: list[SocialUserResponse] = []
    incoming: list[FriendRequestResponse] = []
    outgoing: list[FriendRequestResponse] = []
    for friendship in relationships:
        other_id = _other_user_id(friendship, user.id)
        other = await _social_user(session, other_id)
        if friendship.status == "accepted":
            friends.append(other)
        else:
            request = FriendRequestResponse(
                id=friendship.id, user=other, created_at=friendship.created_at
            )
            (outgoing if friendship.requested_by_id == user.id else incoming).append(request)
    return SocialOverviewResponse(friends=friends, incoming=incoming, outgoing=outgoing)


@router.post("/friend-requests", response_model=FriendRequestResponse, status_code=201)
async def send_friend_request(
    request: FriendRequestCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> FriendRequestResponse:
    email = request.email.strip().lower()
    target = (
        await session.execute(select(UserModel).where(UserModel.email == email))
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bu e-postayla kullanıcı yok."
        )
    if target.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Kendine arkadaşlık isteği gönderemezsin.",
        )
    low_id, high_id = _ordered_pair(user.id, target.id)
    existing = (
        await session.execute(
            select(FriendshipModel).where(
                FriendshipModel.user_low_id == low_id,
                FriendshipModel.user_high_id == high_id,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        if existing.status == "accepted":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zaten arkadaşsınız.")
        if existing.requested_by_id == target.id:
            existing.status = "accepted"
            existing.accepted_at = datetime.now(UTC)
            await session.commit()
            return FriendRequestResponse(
                id=existing.id,
                user=await _social_user(session, target.id),
                created_at=existing.created_at,
            )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="İstek zaten gönderilmiş.")
    friendship = FriendshipModel(
        user_low_id=low_id, user_high_id=high_id, requested_by_id=user.id, status="pending"
    )
    session.add(friendship)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="İstek zaten mevcut."
        ) from error
    await session.refresh(friendship)
    return FriendRequestResponse(
        id=friendship.id,
        user=await _social_user(session, target.id),
        created_at=friendship.created_at,
    )


@router.post("/friend-requests/{request_id}/accept", status_code=204)
async def accept_friend_request(
    request_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    friendship = await session.get(FriendshipModel, request_id)
    if (
        friendship is None
        or friendship.status != "pending"
        or friendship.requested_by_id == user.id
        or user.id not in (friendship.user_low_id, friendship.user_high_id)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İstek bulunamadı.")
    friendship.status = "accepted"
    friendship.accepted_at = datetime.now(UTC)
    await session.commit()


@router.delete("/friendships/{friendship_id}", status_code=204)
async def remove_friendship(
    friendship_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    friendship = await session.get(FriendshipModel, friendship_id)
    if friendship is None or user.id not in (friendship.user_low_id, friendship.user_high_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bağlantı bulunamadı.")
    await session.delete(friendship)
    await session.commit()


@router.get("/messages/{friend_user_id}", response_model=list[MessageResponse])
async def list_messages(
    friend_user_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> list[MessageResponse]:
    friendship = await _accepted_friendship(session, user.id, friend_user_id)
    messages = (
        await session.execute(
            select(DirectMessageModel)
            .where(DirectMessageModel.friendship_id == friendship.id)
            .order_by(DirectMessageModel.created_at.desc())
            .limit(100)
        )
    ).scalars().all()
    return [_message_response(item, current_user_id=user.id) for item in reversed(messages)]


@router.post("/messages/{friend_user_id}", response_model=MessageResponse, status_code=201)
async def send_message(
    friend_user_id: uuid.UUID,
    request: MessageCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> MessageResponse:
    friendship = await _accepted_friendship(session, user.id, friend_user_id)
    message = DirectMessageModel(
        friendship_id=friendship.id, sender_id=user.id, body=request.body.strip()
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return _message_response(message, current_user_id=user.id)


async def _accepted_friendship(
    session: AsyncSession, user_id: uuid.UUID, other_id: uuid.UUID
) -> FriendshipModel:
    low_id, high_id = _ordered_pair(user_id, other_id)
    friendship = (
        await session.execute(
            select(FriendshipModel).where(
                FriendshipModel.user_low_id == low_id,
                FriendshipModel.user_high_id == high_id,
                FriendshipModel.status == "accepted",
            )
        )
    ).scalar_one_or_none()
    if friendship is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Önce arkadaş olmalısınız."
        )
    return friendship


async def _social_user(session: AsyncSession, user_id: uuid.UUID) -> SocialUserResponse:
    user = await session.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")
    profile = (
        await session.execute(select(BirthProfileModel).where(BirthProfileModel.user_id == user_id))
    ).scalar_one_or_none()
    return SocialUserResponse(
        id=user.id,
        display_name=profile.name if profile else user.email.split("@", 1)[0],
        email=user.email,
    )


def _ordered_pair(first: uuid.UUID, second: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    return (first, second) if first.int < second.int else (second, first)


def _other_user_id(friendship: FriendshipModel, current_user_id: uuid.UUID) -> uuid.UUID:
    return (
        friendship.user_high_id
        if friendship.user_low_id == current_user_id
        else friendship.user_low_id
    )


def _message_response(
    message: DirectMessageModel, *, current_user_id: uuid.UUID
) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        body=message.body,
        created_at=message.created_at,
        is_mine=message.sender_id == current_user_id,
    )
