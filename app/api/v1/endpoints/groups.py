import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.endpoints.social import _accepted_friendship, _social_user
from app.api.v1.schemas.groups import (
    GroupCreate,
    GroupMemberResponse,
    GroupMessageCreate,
    GroupMessageResponse,
    GroupResponse,
)
from app.core.config import get_settings
from app.core.content_moderation import ensure_allowed_user_content
from app.core.database import get_database_session
from app.modules.astrology.infrastructure.models import (
    FirebaseInstallationModel,
    GroupMemberModel,
    GroupMessageModel,
    GroupModel,
    UserModel,
)
from app.modules.notifications.service import get_firebase_push_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/social/groups")


@router.get("", response_model=list[GroupResponse])
async def list_groups(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> list[GroupResponse]:
    memberships = (
        await session.execute(
            select(GroupMemberModel)
            .where(GroupMemberModel.user_id == user.id)
            .order_by(GroupMemberModel.joined_at.desc())
        )
    ).scalars().all()
    return [await _group_response(session, item.group_id, user.id, item) for item in memberships]


@router.post("", response_model=GroupResponse, status_code=201)
async def create_group(
    request: GroupCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> GroupResponse:
    member_ids = [item for item in request.member_ids if item != user.id]
    for member_id in member_ids:
        await _accepted_friendship(session, user.id, member_id)
    group = GroupModel(name=request.name, owner_id=user.id)
    session.add(group)
    await session.flush()
    owner_membership = GroupMemberModel(group_id=group.id, user_id=user.id, role="owner")
    session.add(owner_membership)
    session.add_all(
        GroupMemberModel(group_id=group.id, user_id=member_id, role="member")
        for member_id in member_ids
    )
    await session.commit()
    return await _group_response(session, group.id, user.id, owner_membership)


@router.get("/{group_id}/messages", response_model=list[GroupMessageResponse])
async def list_group_messages(
    group_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> list[GroupMessageResponse]:
    membership = await _membership(session, group_id, user.id)
    messages = (
        await session.execute(
            select(GroupMessageModel)
            .where(GroupMessageModel.group_id == group_id)
            .order_by(GroupMessageModel.created_at.desc())
            .limit(100)
        )
    ).scalars().all()
    membership.last_read_at = datetime.now(UTC)
    await session.commit()
    return [await _message_response(session, item, user.id) for item in reversed(messages)]


@router.post("/{group_id}/messages", response_model=GroupMessageResponse, status_code=201)
async def send_group_message(
    group_id: uuid.UUID,
    request: GroupMessageCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> GroupMessageResponse:
    membership = await _membership(session, group_id, user.id)
    recent_messages = await session.scalar(
        select(func.count(GroupMessageModel.id)).where(
            GroupMessageModel.sender_id == user.id,
            GroupMessageModel.created_at >= datetime.now(UTC) - timedelta(minutes=1),
        )
    ) or 0
    if recent_messages >= get_settings().messages_per_minute:
        raise HTTPException(status_code=429, detail="Çok hızlı mesaj gönderiyorsun.")
    message = GroupMessageModel(
        group_id=group_id,
        sender_id=user.id,
        body=ensure_allowed_user_content(request.body),
    )
    session.add(message)
    membership.last_read_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(message)
    recipients = list(
        (
            await session.execute(
                select(FirebaseInstallationModel.fid)
                .join(
                    GroupMemberModel,
                    GroupMemberModel.user_id == FirebaseInstallationModel.user_id,
                )
                .where(GroupMemberModel.group_id == group_id, GroupMemberModel.user_id != user.id)
            )
        ).scalars()
    )
    if recipients:
        try:
            group = await session.get(GroupModel, group_id)
            sender = await _social_user(session, user.id)
            await get_firebase_push_service().send_new_message(
                fids=recipients,
                sender_name=f"{group.name if group else 'Grup'} · {sender.display_name}",
                message_preview=message.body,
            )
        except Exception:
            logger.exception("Group push notification could not be sent")
    return await _message_response(session, message, user.id)


@router.delete("/{group_id}/membership", status_code=204)
async def leave_group(
    group_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    membership = await _membership(session, group_id, user.id)
    group = await session.get(GroupModel, group_id)
    if group is not None and group.owner_id == user.id:
        await session.delete(group)
    else:
        await session.delete(membership)
    await session.commit()


async def _membership(
    session: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID
) -> GroupMemberModel:
    membership = (
        await session.execute(
            select(GroupMemberModel).where(
                GroupMemberModel.group_id == group_id, GroupMemberModel.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grup bulunamadı.")
    return membership


async def _group_response(
    session: AsyncSession,
    group_id: uuid.UUID,
    current_user_id: uuid.UUID,
    membership: GroupMemberModel | None = None,
) -> GroupResponse:
    group = await session.get(GroupModel, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Grup bulunamadı.")
    rows = (
        await session.execute(
            select(GroupMemberModel)
            .where(GroupMemberModel.group_id == group_id)
            .order_by(GroupMemberModel.joined_at)
        )
    ).scalars().all()
    current = membership or next(item for item in rows if item.user_id == current_user_id)
    unread = await session.scalar(
        select(func.count(GroupMessageModel.id)).where(
            GroupMessageModel.group_id == group_id,
            GroupMessageModel.sender_id != current_user_id,
            GroupMessageModel.created_at > (current.last_read_at or current.joined_at),
        )
    ) or 0
    return GroupResponse(
        id=group.id,
        name=group.name,
        owner_id=group.owner_id,
        members=[
            GroupMemberResponse(user=await _social_user(session, row.user_id), role=row.role)
            for row in rows
        ],
        unread_count=unread,
        created_at=group.created_at,
    )


async def _message_response(
    session: AsyncSession, message: GroupMessageModel, current_user_id: uuid.UUID
) -> GroupMessageResponse:
    return GroupMessageResponse(
        id=message.id,
        sender=await _social_user(session, message.sender_id),
        body=message.body,
        created_at=message.created_at,
        is_mine=message.sender_id == current_user_id,
    )
