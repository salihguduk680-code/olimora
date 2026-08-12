import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.dependencies import get_ephemeris_calculator
from app.api.v1.schemas.persisted_chart import (
    NatalChartCreateRequest,
    PersistedNatalChartResponse,
)
from app.core.database import get_database_session
from app.modules.astrology.application.calculate_natal_chart import (
    BirthProfileNotFoundError,
    CalculateNatalChart,
)
from app.modules.astrology.application.constants import NATAL_CHART_SCHEMA_VERSION
from app.modules.astrology.domain.exceptions import EphemerisCalculationError
from app.modules.astrology.domain.ports import EphemerisCalculator
from app.modules.astrology.infrastructure.models import BirthProfileModel, UserModel
from app.modules.astrology.infrastructure.repository import AstrologyRepository

router = APIRouter()


@router.post(
    "/birth-profiles/{profile_id}/natal-chart",
    response_model=PersistedNatalChartResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {
            "model": PersistedNatalChartResponse,
            "description": "Existing deterministic chart returned from cache.",
        }
    },
)
async def create_natal_chart(
    profile_id: uuid.UUID,
    request: NatalChartCreateRequest,
    response: Response,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
    ephemeris: Annotated[EphemerisCalculator, Depends(get_ephemeris_calculator)],
) -> PersistedNatalChartResponse:
    profile = await session.get(BirthProfileModel, profile_id)
    if profile is None or profile.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth profile not found.",
        )
    use_case = CalculateNatalChart(AstrologyRepository(session), ephemeris)
    try:
        outcome = await use_case.execute(
            profile_id=profile_id,
            house_system=request.house_system,
        )
    except BirthProfileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth profile not found.",
        ) from error
    except EphemerisCalculationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "EPHEMERIS_CALCULATION_ERROR", "message": str(error)},
        ) from error

    response.status_code = (
        status.HTTP_201_CREATED if outcome.status == "calculated" else status.HTTP_200_OK
    )
    return PersistedNatalChartResponse(
        schema_version=NATAL_CHART_SCHEMA_VERSION,
        chart_id=outcome.chart_id,
        profile_id=outcome.profile_id,
        input_hash=outcome.input_hash,
        status=outcome.status,
        result=outcome.result,
    )
