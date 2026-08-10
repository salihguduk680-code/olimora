from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.schemas.notifications import (
    FirebaseInstallationCreate,
    FirebaseInstallationResponse,
)
from app.core.database import get_database_session
from app.modules.astrology.infrastructure.models import FirebaseInstallationModel, UserModel

router = APIRouter(prefix="/notifications")


@router.put("/installation", response_model=FirebaseInstallationResponse)
async def register_installation(
    request: FirebaseInstallationCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> FirebaseInstallationResponse:
    fid = request.fid.strip()
    installation = (
        await session.execute(
            select(FirebaseInstallationModel).where(FirebaseInstallationModel.fid == fid)
        )
    ).scalar_one_or_none()
    if installation is None:
        installation = FirebaseInstallationModel(
            user_id=user.id,
            fid=fid,
            platform=request.platform,
        )
        session.add(installation)
    else:
        installation.user_id = user.id
        installation.platform = request.platform
        installation.updated_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(installation)
    return FirebaseInstallationResponse(
        id=installation.id,
        fid=installation.fid,
        platform=installation.platform,
        updated_at=installation.updated_at,
    )
