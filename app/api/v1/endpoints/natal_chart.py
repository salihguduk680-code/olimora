from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_ephemeris_calculator
from app.api.v1.schemas.natal_chart import (
    AspectResponse,
    ChartPointResponse,
    HouseCuspResponse,
    NatalChartPreviewRequest,
    NatalChartPreviewResponse,
)
from app.modules.astrology.application.constants import NATAL_CHART_SCHEMA_VERSION
from app.modules.astrology.application.input_hasher import create_natal_chart_input_hash
from app.modules.astrology.application.timezone_resolver import resolve_local_datetime
from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    EphemerisCalculationError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)
from app.modules.astrology.domain.ports import EphemerisCalculator

router = APIRouter()


def _point_response(point: object) -> ChartPointResponse:
    from app.modules.astrology.domain.natal_chart import ChartPoint

    if not isinstance(point, ChartPoint):
        raise TypeError("Expected ChartPoint.")
    return ChartPointResponse(
        name=point.name,
        longitude=point.longitude,
        latitude=point.latitude,
        distance=point.distance,
        sign=point.sign,
        degree_in_sign=point.degree_in_sign,
        speed_longitude=point.speed_longitude,
        is_retrograde=point.is_retrograde,
        house=point.house,
    )


@router.post("/natal-chart/preview", response_model=NatalChartPreviewResponse)
async def preview_natal_chart(
    request: NatalChartPreviewRequest,
    ephemeris: Annotated[EphemerisCalculator, Depends(get_ephemeris_calculator)],
) -> NatalChartPreviewResponse:
    try:
        resolved = resolve_local_datetime(
            local_datetime=request.local_datetime,
            timezone_name=request.timezone_name,
            fold=request.fold,
            utc_offset_minutes=request.utc_offset_minutes,
        )
        config = ephemeris.get_calculation_config(house_system=request.house_system)
        chart = ephemeris.calculate_natal_chart(
            utc_datetime=resolved.utc_datetime,
            latitude=request.latitude,
            longitude=request.longitude,
            house_system=request.house_system,
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
    except EphemerisCalculationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "EPHEMERIS_CALCULATION_ERROR", "message": str(error)},
        ) from error

    return NatalChartPreviewResponse(
        schema_version=NATAL_CHART_SCHEMA_VERSION,
        input_hash=create_natal_chart_input_hash(
            resolved_utc_datetime=resolved.utc_datetime,
            latitude=request.latitude,
            longitude=request.longitude,
            house_system=request.house_system,
            requested_bodies=config.requested_bodies,
            calculator_name=config.calculator_name,
            engine_version=config.engine_version,
            wrapper_version=config.wrapper_version,
            calculation_flags=config.calculation_flags,
            zodiac_type=config.zodiac_type,
            house_placement_method=config.house_placement_method,
            schema_version=NATAL_CHART_SCHEMA_VERSION,
        ),
        local_datetime=request.local_datetime,
        timezone_name=request.timezone_name,
        resolved_utc_datetime=chart.utc_datetime,
        julian_day_ut=chart.julian_day_ut,
        latitude=chart.latitude,
        longitude=chart.longitude,
        place_name=request.place_name,
        house_system=chart.house_system,
        engine_name=chart.engine_name,
        engine_version=chart.engine_version,
        calculation_flags=chart.calculation_flags,
        sun=_point_response(chart.sun),
        moon=_point_response(chart.moon),
        ascendant=_point_response(chart.ascendant),
        positions=[_point_response(point) for point in chart.positions],
        houses=[
            HouseCuspResponse(
                house_number=house.house_number,
                longitude=house.longitude,
                sign=house.sign,
                degree_in_sign=house.degree_in_sign,
            )
            for house in chart.houses
        ],
        aspects=[
            AspectResponse(
                body_a=aspect.body_a,
                body_b=aspect.body_b,
                aspect_type=aspect.aspect_type,
                exact_angle=aspect.exact_angle,
                actual_angle=aspect.actual_angle,
                orb=aspect.orb,
            )
            for aspect in chart.aspects
        ],
    )
