import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BirthProfileCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    local_datetime: datetime
    timezone_name: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    place_name: str = Field(min_length=1, max_length=200)
    fold: int | None = Field(default=None, ge=0, le=1)
    utc_offset_minutes: int | None = Field(default=None, ge=-840, le=840)

    @field_validator("name", "place_name")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class BirthProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    local_datetime: datetime
    timezone_name: str
    resolved_utc_datetime: datetime
    fold: int
    utc_offset_minutes: int
    latitude: float
    longitude: float
    place_name: str
    tzdata_version: str
    created_at: datetime
