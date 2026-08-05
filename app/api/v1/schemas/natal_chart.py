from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class NatalChartPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    local_datetime: datetime
    timezone_name: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    place_name: str = Field(min_length=1, max_length=200)
    fold: int | None = Field(default=None, ge=0, le=1)
    utc_offset_minutes: int | None = Field(default=None, ge=-840, le=840)
    house_system: Literal["P"] = "P"


class ChartPointResponse(BaseModel):
    name: str
    longitude: float
    latitude: float | None
    distance: float | None
    sign: str
    degree_in_sign: float
    speed_longitude: float | None
    is_retrograde: bool | None
    house: int | None


class HouseCuspResponse(BaseModel):
    house_number: int
    longitude: float
    sign: str
    degree_in_sign: float


class AspectResponse(BaseModel):
    body_a: str
    body_b: str
    aspect_type: str
    exact_angle: float
    actual_angle: float
    orb: float


class NatalChartPreviewResponse(BaseModel):
    schema_version: str
    input_hash: str
    local_datetime: datetime
    timezone_name: str
    resolved_utc_datetime: datetime
    julian_day_ut: float
    latitude: float
    longitude: float
    place_name: str
    house_system: str
    engine_name: str
    engine_version: str
    calculation_flags: int
    sun: ChartPointResponse
    moon: ChartPointResponse
    ascendant: ChartPointResponse
    positions: list[ChartPointResponse]
    houses: list[HouseCuspResponse]
    aspects: list[AspectResponse]
