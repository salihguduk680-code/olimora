import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.schemas.moderation import (
    AthenaFeedbackCreate,
    ModerationActionResponse,
    ProductFeedbackCreate,
    UserReportCreate,
)
from app.core.database import get_database_session
from app.modules.astrology.infrastructure.models import (
    ContentFeedbackModel,
    DirectMessageModel,
    FriendshipModel,
    ProductFeedbackModel,
    UserBlockModel,
    UserModel,
    UserReportModel,
)

router = APIRouter(prefix="/moderation")


@router.post("/reports", response_model=ModerationActionResponse, status_code=201)
async def report_user(
    request: UserReportCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ModerationActionResponse:
    if request.reported_user_id == user.id:
        raise HTTPException(status_code=422, detail="Kendini bildiremezsin.")
    if await session.get(UserModel, request.reported_user_id) is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    recent = (
        await session.scalar(
            select(func.count(UserReportModel.id)).where(
                UserReportModel.reporter_id == user.id,
                UserReportModel.created_at >= datetime.now(UTC) - timedelta(days=1),
            )
        )
        or 0
    )
    if recent >= 20:
        raise HTTPException(status_code=429, detail="Bugün çok fazla bildirim gönderdin.")
    if request.message_id is not None:
        message = await session.get(DirectMessageModel, request.message_id)
        if message is None or message.sender_id != request.reported_user_id:
            raise HTTPException(status_code=404, detail="Bildirilecek mesaj bulunamadı.")
        friendship = await session.get(FriendshipModel, message.friendship_id)
        if friendship is None or user.id not in (friendship.user_low_id, friendship.user_high_id):
            raise HTTPException(status_code=403, detail="Bu mesajı bildiremezsin.")
    session.add(
        UserReportModel(
            reporter_id=user.id,
            reported_user_id=request.reported_user_id,
            message_id=request.message_id,
            reason=request.reason,
            details=request.details,
        )
    )
    await session.commit()
    return ModerationActionResponse(status="received")


@router.post("/blocks/{blocked_user_id}", response_model=ModerationActionResponse, status_code=201)
async def block_user(
    blocked_user_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ModerationActionResponse:
    if blocked_user_id == user.id:
        raise HTTPException(status_code=422, detail="Kendini engelleyemezsin.")
    if await session.get(UserModel, blocked_user_id) is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    existing = (
        await session.execute(
            select(UserBlockModel).where(
                UserBlockModel.blocker_id == user.id,
                UserBlockModel.blocked_id == blocked_user_id,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        session.add(UserBlockModel(blocker_id=user.id, blocked_id=blocked_user_id))
    low_id, high_id = sorted((user.id, blocked_user_id), key=lambda item: item.int)
    await session.execute(
        delete(FriendshipModel).where(
            FriendshipModel.user_low_id == low_id,
            FriendshipModel.user_high_id == high_id,
        )
    )
    await session.commit()
    return ModerationActionResponse(status="blocked")


@router.delete("/blocks/{blocked_user_id}", status_code=204)
async def unblock_user(
    blocked_user_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    await session.execute(
        delete(UserBlockModel).where(
            UserBlockModel.blocker_id == user.id,
            UserBlockModel.blocked_id == blocked_user_id,
        )
    )
    await session.commit()


@router.post("/athena-feedback", response_model=ModerationActionResponse, status_code=201)
async def submit_athena_feedback(
    request: AthenaFeedbackCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ModerationActionResponse:
    session.add(
        ContentFeedbackModel(
            user_id=user.id,
            content_type=request.content_type,
            reason=request.reason,
            details=request.details,
        )
    )
    await session.commit()
    return ModerationActionResponse(status="received")


@router.post("/product-feedback", response_model=ModerationActionResponse, status_code=201)
async def submit_product_feedback(
    request: ProductFeedbackCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ModerationActionResponse:
    recent = (
        await session.scalar(
            select(func.count(ProductFeedbackModel.id)).where(
                ProductFeedbackModel.user_id == user.id,
                ProductFeedbackModel.created_at >= datetime.now(UTC) - timedelta(days=1),
            )
        )
        or 0
    )
    if recent >= 5:
        raise HTTPException(status_code=429, detail="Bugün yeterince geri bildirim gönderdin.")
    session.add(
        ProductFeedbackModel(
            user_id=user.id,
            category=request.category,
            rating=request.rating,
            details=request.details,
        )
    )
    await session.commit()
    return ModerationActionResponse(status="received")


async def blocked_user_ids(session: AsyncSession, user_id: uuid.UUID) -> set[uuid.UUID]:
    rows = await session.execute(
        select(UserBlockModel.blocker_id, UserBlockModel.blocked_id).where(
            or_(UserBlockModel.blocker_id == user_id, UserBlockModel.blocked_id == user_id)
        )
    )
    return {blocked_id if blocker_id == user_id else blocker_id for blocker_id, blocked_id in rows}
