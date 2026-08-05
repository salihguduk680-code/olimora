from datetime import date

from pydantic import BaseModel, ConfigDict

from app.modules.astrology.domain.enums import ZodiacSign


class SunSignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth_date: date


class SunSignResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth_date: date
    sign: ZodiacSign
    method: str
    schema_version: str
    requires_exact_calculation: bool
    note: str | None
