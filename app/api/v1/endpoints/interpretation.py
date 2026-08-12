import hashlib
import json
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from datetime import time as datetime_time
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.dependencies import get_athena_interpretation_service, get_ephemeris_calculator
from app.api.v1.schemas.daily_reading import DailyReadingResponse, DailySignReadingResponse
from app.api.v1.schemas.interpretation import (
    AthenaInterpretationRequest,
    AthenaInterpretationResponse,
)
from app.core.config import get_settings
from app.core.database import get_database_session
from app.modules.astrology.application.timezone_resolver import resolve_local_datetime
from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    EphemerisCalculationError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)
from app.modules.astrology.domain.ports import EphemerisCalculator
from app.modules.astrology.infrastructure.models import (
    BirthProfileModel,
    DailyReadingModel,
    DailySignReadingModel,
    NatalInterpretationModel,
    UserModel,
)
from app.modules.interpretation.service import (
    AthenaInterpretationService,
    InterpretationUnavailableError,
)

router = APIRouter()
_request_times: defaultdict[str, deque[float]] = defaultdict(deque)


@router.post("/daily-sign", response_model=DailySignReadingResponse)
async def create_daily_sign_reading(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
    ephemeris: Annotated[EphemerisCalculator, Depends(get_ephemeris_calculator)],
    athena: Annotated[AthenaInterpretationService, Depends(get_athena_interpretation_service)],
) -> DailySignReadingResponse:
    profile = (
        await session.execute(select(BirthProfileModel).where(BirthProfileModel.user_id == user.id))
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Günlük burç yorumu için önce doğum bilgilerini kaydet.",
        )
    try:
        timezone = ZoneInfo(profile.timezone_name)
    except ZoneInfoNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Kayıtlı saat dilimi geçersiz.",
        ) from error

    reading_date = datetime.now(UTC).astimezone(timezone).date()
    try:
        natal_chart = ephemeris.calculate_natal_chart(
            utc_datetime=profile.resolved_utc_datetime,
            latitude=profile.latitude,
            longitude=profile.longitude,
            house_system="P",
        )
    except EphemerisCalculationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Güneş burcu hesaplanamadı.",
        ) from error
    sign = natal_chart.sun.sign

    # Aynı tarih ve burç için bütün kullanıcılar tek üretimi paylaşır.
    lock_key = f"daily-sign:{reading_date.isoformat()}:{sign}"
    await session.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": lock_key})
    existing = (
        await session.execute(
            select(DailySignReadingModel).where(
                DailySignReadingModel.reading_date == reading_date,
                DailySignReadingModel.sign == sign,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return _daily_sign_response(existing, cached=True)

    try:
        global_noon = datetime.combine(reading_date, datetime_time(hour=12), tzinfo=UTC)
        transit_chart = ephemeris.calculate_natal_chart(
            utc_datetime=global_noon,
            latitude=0.0,
            longitude=0.0,
            house_system="P",
        )
    except EphemerisCalculationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Günün gökyüzü hesaplanamadı.",
        ) from error

    previous = (
        await session.execute(
            select(DailySignReadingModel)
            .where(
                DailySignReadingModel.sign == sign,
                DailySignReadingModel.reading_date < reading_date,
            )
            .order_by(DailySignReadingModel.reading_date.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    previous_text = None
    if previous is not None:
        previous_text = " | ".join(
            (previous.main_theme, previous.relationships, previous.work_money, previous.caution)
        )
    try:
        result = await athena.interpret_daily_sign(
            sign=sign,
            reading_date=reading_date.isoformat(),
            transit_chart=transit_chart,
            previous_reading=previous_text,
        )
        values: dict[str, str | None] = {
            "main_theme": result.main_theme,
            "relationships": result.relationships,
            "work_money": result.work_money,
            "caution": result.caution,
            "source": "openai",
            "model": result.model,
        }
    except InterpretationUnavailableError:
        values = _daily_fallback(sign, transit_chart.moon.sign)

    reading = DailySignReadingModel(reading_date=reading_date, sign=sign, **values)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return _daily_sign_response(reading, cached=False)


@router.post("/daily", response_model=DailyReadingResponse)
async def create_daily_reading(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
    ephemeris: Annotated[EphemerisCalculator, Depends(get_ephemeris_calculator)],
    athena: Annotated[AthenaInterpretationService, Depends(get_athena_interpretation_service)],
) -> DailyReadingResponse:
    profile = (
        await session.execute(select(BirthProfileModel).where(BirthProfileModel.user_id == user.id))
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Günlük yorum için önce doğum bilgilerini kaydet.",
        )
    try:
        timezone = ZoneInfo(profile.timezone_name)
    except ZoneInfoNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Kayıtlı saat dilimi geçersiz.",
        ) from error
    local_now = datetime.now(UTC).astimezone(timezone)
    reading_date = local_now.date()

    # Aynı kullanıcı aynı anda iki kez dokunsa bile yalnızca bir AI isteği üret.
    lock_key = f"daily:{user.id}:{reading_date.isoformat()}"
    await session.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": lock_key})
    existing = (
        await session.execute(
            select(DailyReadingModel).where(
                DailyReadingModel.user_id == user.id,
                DailyReadingModel.reading_date == reading_date,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return _daily_response(existing, cached=True)

    try:
        natal_chart = ephemeris.calculate_natal_chart(
            utc_datetime=profile.resolved_utc_datetime,
            latitude=profile.latitude,
            longitude=profile.longitude,
            house_system="P",
        )
        local_noon = datetime.combine(reading_date, datetime_time(hour=12), tzinfo=timezone)
        transit_chart = ephemeris.calculate_natal_chart(
            utc_datetime=local_noon.astimezone(UTC),
            latitude=profile.latitude,
            longitude=profile.longitude,
            house_system="P",
        )
    except EphemerisCalculationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Günün gökyüzü hesaplanamadı.",
        ) from error

    try:
        result = await athena.interpret_daily(
            name=profile.name,
            place_name=profile.place_name,
            natal_chart=natal_chart,
            transit_chart=transit_chart,
        )
        values: dict[str, str | None] = {
            "main_theme": result.main_theme,
            "relationships": result.relationships,
            "work_money": result.work_money,
            "caution": result.caution,
            "source": "openai",
            "model": result.model,
        }
    except InterpretationUnavailableError:
        values = _daily_fallback(natal_chart.sun.sign, transit_chart.moon.sign)

    reading = DailyReadingModel(user_id=user.id, reading_date=reading_date, **values)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return _daily_response(reading, cached=False)


def _daily_response(reading: DailyReadingModel, *, cached: bool) -> DailyReadingResponse:
    return DailyReadingResponse(
        reading_date=reading.reading_date,
        main_theme=reading.main_theme,
        relationships=reading.relationships,
        work_money=reading.work_money,
        caution=reading.caution,
        source=reading.source,  # type: ignore[arg-type]
        model=reading.model,
        cached=cached,
    )


def _daily_sign_response(
    reading: DailySignReadingModel, *, cached: bool
) -> DailySignReadingResponse:
    return DailySignReadingResponse(
        reading_date=reading.reading_date,
        sign=reading.sign,
        main_theme=reading.main_theme,
        relationships=reading.relationships,
        work_money=reading.work_money,
        caution=reading.caution,
        source=reading.source,  # type: ignore[arg-type]
        model=reading.model,
        cached=cached,
    )


def _daily_fallback(sun_sign: str, transit_moon_sign: str) -> dict[str, str | None]:
    return {
        "main_theme": (
            f"{sun_sign} Güneşinin temel yaklaşımı bugün iç ritmini dinlemeyi destekleyebilir."
        ),
        "relationships": (
            "İlişkilerde varsayım yapmak yerine açık ve sakin bir konuşma faydalı olabilir."
        ),
        "work_money": (
            "Önceliklerini sadeleştirip tamamlanabilir bir işe odaklanmak verimini artırabilir."
        ),
        "caution": (
            f"Günün Ayı {transit_moon_sign} burcundayken ilk tepkinle kararın arasına "
            "kısa bir mola koy."
        ),
        "source": "fallback",
        "model": None,
    }


@router.post("/natal-chart/interpret", response_model=AthenaInterpretationResponse)
async def interpret_natal_chart(
    request: AthenaInterpretationRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
    ephemeris: Annotated[EphemerisCalculator, Depends(get_ephemeris_calculator)],
    athena: Annotated[AthenaInterpretationService, Depends(get_athena_interpretation_service)],
) -> AthenaInterpretationResponse:
    _enforce_rate_limit(str(user.id))
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

    input_hash = hashlib.sha256(
        json.dumps(
            request.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    await session.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
        {"key": f"natal-interpretation:{user.id}:{input_hash}"},
    )
    cached = (
        await session.execute(
            select(NatalInterpretationModel).where(
                NatalInterpretationModel.user_id == user.id,
                NatalInterpretationModel.input_hash == input_hash,
            )
        )
    ).scalar_one_or_none()
    if cached is not None:
        return AthenaInterpretationResponse(
            interpretation=cached.interpretation,
            source=cached.source,  # type: ignore[arg-type]
            model=cached.model,
            cached=True,
        )

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
    interpretation = NatalInterpretationModel(
        user_id=user.id,
        input_hash=input_hash,
        interpretation=result.text,
        source="openai",
        model=result.model,
    )
    session.add(interpretation)
    await session.commit()
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
