from fastapi import APIRouter

from app.api.v1.schemas.sun_sign import SunSignRequest, SunSignResponse
from app.modules.astrology.domain.sun_sign import calculate_conventional_sun_sign

router = APIRouter()


@router.post("/sun-sign", response_model=SunSignResponse)
async def sun_sign(request: SunSignRequest) -> SunSignResponse:
    result = calculate_conventional_sun_sign(request.birth_date)
    return SunSignResponse(
        birth_date=request.birth_date,
        sign=result.sign,
        method=result.method,
        schema_version=result.schema_version,
        requires_exact_calculation=result.requires_exact_calculation,
        note=result.note,
    )
