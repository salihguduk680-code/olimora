import importlib.metadata
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_ephemeris_calculator
from app.core.config import get_settings
from app.core.database import get_database_session
from app.modules.astrology.domain.ports import EphemerisCalculator

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]
    ephemeris: Literal["ok"]
    app_version: str
    wrapper_version: str
    engine_version: str
    tzdata_version: str


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    ephemeris: Annotated[EphemerisCalculator, Depends(get_ephemeris_calculator)],
) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "DATABASE_UNAVAILABLE", "message": "Database health check failed."},
        ) from error

    return HealthResponse(
        status="ok",
        database="ok",
        ephemeris="ok",
        app_version=get_settings().app_version,
        wrapper_version=importlib.metadata.version("pysweph"),
        engine_version=ephemeris.get_calculation_config(house_system="P").engine_version,
        tzdata_version=importlib.metadata.version("tzdata"),
    )
