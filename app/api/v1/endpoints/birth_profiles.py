from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.birth_profile import BirthProfileCreateRequest, BirthProfileResponse
from app.core.database import get_database_session
from app.modules.astrology.application.create_birth_profile import CreateBirthProfile
from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)
from app.modules.astrology.infrastructure.repository import AstrologyRepository

router = APIRouter()


@router.post("/birth-profiles", response_model=BirthProfileResponse, status_code=201)
async def create_birth_profile(
    request: BirthProfileCreateRequest,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> BirthProfileResponse:
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

    return BirthProfileResponse(
        id=profile.id,
        name=profile.name,
        local_datetime=profile.local_birth_datetime_naive,
        timezone_name=profile.timezone_name,
        resolved_utc_datetime=profile.resolved_utc_datetime,
        fold=profile.fold,
        utc_offset_minutes=profile.utc_offset_minutes,
        latitude=profile.latitude,
        longitude=profile.longitude,
        place_name=profile.place_name,
        tzdata_version=profile.tzdata_version,
        created_at=profile.created_at,
    )
