import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies import get_athena_interpretation_service, get_ephemeris_calculator
from app.api.v1.schemas.interpretation import (
    AthenaInterpretationRequest,
    AthenaInterpretationResponse,
)
from app.core.config import get_settings
from app.modules.astrology.application.timezone_resolver import resolve_local_datetime
from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    EphemerisCalculationError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)
from app.modules.astrology.domain.ports import EphemerisCalculator
from app.modules.interpretation.service import (
    AthenaInterpretationService,
    InterpretationUnavailableError,
)

router = APIRouter()
_request_times: defaultdict[str, deque[float]] = defaultdict(deque)


@router.post("/natal-chart/interpret", response_model=AthenaInterpretationResponse)
async def interpret_natal_chart(
    request: AthenaInterpretationRequest,
    http_request: Request,
    ephemeris: Annotated[EphemerisCalculator, Depends(get_ephemeris_calculator)],
    athena: Annotated[AthenaInterpretationService, Depends(get_athena_interpretation_service)],
) -> AthenaInterpretationResponse:
    _enforce_rate_limit(http_request.client.host if http_request.client else "unknown")
    try:
        resolved = resolve_local_datetime(
            local_datetime=request.local_datetime,
            timezone_name=request.timezone_name,
            fold=request.fold,
            utc_offset_minutes=request.utc_offset_minutes,
        )
        chart = ephemeris.calculate_natal_chart(
            utc_datetime=resolved.utc_datetime,
            latitude=request.latitude,
            longitude=request.longitude,
            house_system=request.house_system,
        )
    except AmbiguousTimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "AMBIGUOUS_LOCAL_TIME", "message": str(error)},
        ) from error
    except (NonExistentTimeError, InvalidLocalDateTimeError, EphemerisCalculationError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_CHART_INPUT", "message": str(error)},
        ) from error

    try:
        result = await athena.interpret(
            name=request.name,
            place_name=request.place_name,
            chart=chart,
        )
    except InterpretationUnavailableError:
        return AthenaInterpretationResponse(
            interpretation=_fallback_interpretation(
                chart.sun.sign,
                chart.moon.sign,
                chart.ascendant.sign,
            ),
            source="fallback",
        )
    return AthenaInterpretationResponse(
        interpretation=result.text,
        source="openai",
        model=result.model,
    )


def _enforce_rate_limit(client_id: str) -> None:
    now = time.monotonic()
    cutoff = now - 60
    times = _request_times[client_id]
    while times and times[0] < cutoff:
        times.popleft()
    if len(times) >= get_settings().athena_requests_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "ATHENA_RATE_LIMIT", "message": "Bir dakika sonra yeniden dene."},
        )
    times.append(now)


def _fallback_interpretation(sun: str, moon: str, ascendant: str) -> str:
    return (
        f"Güneşinin {sun}, Ayının {moon} ve yükseleninin {ascendant} oluşu; "
        "kendini ifade etme biçimin, duygusal ihtiyaçların ve dışarıya verdiğin ilk izlenim "
        "arasında kendine özgü bir denge kurabileceğini düşündürür. Haritanın ayrıntıları "
        "bu üç ana temanın farklı zamanlarda farklı ağırlıklar kazanabileceğine işaret edebilir."
    )
