from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.schemas.birth_profile import BirthProfileCreateRequest, BirthProfileResponse
from app.core.database import get_database_session
from app.modules.astrology.application.create_birth_profile import CreateBirthProfile
from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)
from app.modules.astrology.infrastructure.models import (
    BirthProfileModel,
    DailyReadingModel,
    NatalInterpretationModel,
    UserModel,
)
from app.modules.astrology.infrastructure.repository import AstrologyRepository

router = APIRouter()


def _remaining_profile_cooldown_hours(
    last_change_at: datetime | None, *, now: datetime
) -> int | None:
    if last_change_at is None:
        return None
    remaining = last_change_at + timedelta(hours=24) - now
    if remaining.total_seconds() <= 0:
        return None
    return max(1, int((remaining.total_seconds() + 3599) // 3600))


def _response(profile: object) -> BirthProfileResponse:
    return BirthProfileResponse(
        id=profile.id,  # type: ignore[attr-defined]
        name=profile.name,  # type: ignore[attr-defined]
        local_datetime=profile.local_birth_datetime_naive,  # type: ignore[attr-defined]
        timezone_name=profile.timezone_name,  # type: ignore[attr-defined]
        resolved_utc_datetime=profile.resolved_utc_datetime,  # type: ignore[attr-defined]
        fold=profile.fold or 0,  # type: ignore[attr-defined]
        utc_offset_minutes=profile.utc_offset_minutes,  # type: ignore[attr-defined]
        latitude=profile.latitude,  # type: ignore[attr-defined]
        longitude=profile.longitude,  # type: ignore[attr-defined]
        place_name=profile.place_name,  # type: ignore[attr-defined]
        tzdata_version=profile.tzdata_version,  # type: ignore[attr-defined]
        created_at=profile.created_at,  # type: ignore[attr-defined]
    )


@router.post("/birth-profiles", response_model=BirthProfileResponse, status_code=201)
async def create_birth_profile(
    request: BirthProfileCreateRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> BirthProfileResponse:
    existing = (
        await session.execute(
            select(BirthProfileModel.id).where(BirthProfileModel.user_id == user.id)
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kayıtlı doğum profilin zaten mevcut.",
        )
    try:
        profile = await CreateBirthProfile(AstrologyRepository(session)).execute(
            name=request.name,
            local_datetime=request.local_datetime,
            timezone_name=request.timezone_name,
            latitude=request.latitude,
            longitude=request.longitude,
            place_name=request.place_name,
            fold=request.fold,
            utc_offset_minutes=request.utc_offset_minutes,
            user_id=user.id,
        )
    except AmbiguousTimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "AMBIGUOUS_LOCAL_TIME",
                "message": str(error),
                "valid_offsets": list(error.valid_offsets),
            },
        ) from error
    except NonExistentTimeError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "NONEXISTENT_LOCAL_TIME", "message": str(error)},
        ) from error
    except InvalidLocalDateTimeError as error:
        code = "INVALID_TIMEZONE" if "timezone" in str(error).lower() else "INVALID_INPUT"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": code, "message": str(error)},
        ) from error

    return _response(profile)


@router.get("/me/birth-profile", response_model=BirthProfileResponse)
async def get_my_birth_profile(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> BirthProfileResponse:
    profile = (
        await session.execute(select(BirthProfileModel).where(BirthProfileModel.user_id == user.id))
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kayıtlı doğum profili yok."
        )
    return _response(profile)


@router.put("/me/birth-profile", response_model=BirthProfileResponse)
async def save_my_birth_profile(
    request: BirthProfileCreateRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> BirthProfileResponse:
    existing = (
        await session.execute(select(BirthProfileModel).where(BirthProfileModel.user_id == user.id))
    ).scalar_one_or_none()
    now = datetime.now(UTC)
    hours = _remaining_profile_cooldown_hours(user.last_birth_profile_change_at, now=now)
    if existing is not None and hours is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Doğum bilgilerini yeniden değiştirmek için yaklaşık "
                f"{hours} saat beklemelisin."
            ),
        )
    await session.execute(delete(DailyReadingModel).where(DailyReadingModel.user_id == user.id))
    await session.execute(
        delete(NatalInterpretationModel).where(NatalInterpretationModel.user_id == user.id)
    )
    if existing is not None:
        user.last_birth_profile_change_at = now
        await session.delete(existing)
        await session.flush()
    try:
        profile = await CreateBirthProfile(AstrologyRepository(session)).execute(
            name=request.name,
            local_datetime=request.local_datetime,
            timezone_name=request.timezone_name,
            latitude=request.latitude,
            longitude=request.longitude,
            place_name=request.place_name,
            fold=request.fold,
            utc_offset_minutes=request.utc_offset_minutes,
            user_id=user.id,
        )
    except (AmbiguousTimeError, NonExistentTimeError, InvalidLocalDateTimeError) as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_BIRTH_TIME", "message": str(error)},
        ) from error
    return _response(profile)
