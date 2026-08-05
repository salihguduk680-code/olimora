from importlib.metadata import version

from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.birth_time import (
    BirthTimeResolveRequest,
    BirthTimeResolveResponse,
)
from app.modules.astrology.application.timezone_resolver import resolve_local_datetime
from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)

router = APIRouter()


@router.post(
    "/birth-time/resolve",
    response_model=BirthTimeResolveResponse,
    status_code=status.HTTP_200_OK,
)
async def resolve_birth_time(request: BirthTimeResolveRequest) -> BirthTimeResolveResponse:
    try:
        result = resolve_local_datetime(
            local_datetime=request.local_datetime,
            timezone_name=request.timezone_name,
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_INPUT", "message": str(error)},
        ) from error

    return BirthTimeResolveResponse(
        local_datetime=request.local_datetime,
        timezone_name=request.timezone_name,
        resolved_utc_datetime=result.utc_datetime,
        fold=result.fold,
        utc_offset_minutes=result.utc_offset_minutes,
        tzdata_version=version("tzdata"),
    )
