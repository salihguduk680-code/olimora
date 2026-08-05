from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BirthTimeResolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    local_datetime: datetime
    timezone_name: str = Field(min_length=1, max_length=100)
    fold: int | None = Field(default=None, ge=0, le=1)
    utc_offset_minutes: int | None = Field(default=None, ge=-840, le=840)


class BirthTimeResolveResponse(BaseModel):
    local_datetime: datetime
    timezone_name: str
    resolved_utc_datetime: datetime
    fold: int
    utc_offset_minutes: int
    tzdata_version: str
