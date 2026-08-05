import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True, slots=True)
class BirthProfile:
    id: uuid.UUID
    user_id: uuid.UUID | None
    name: str
    local_birth_datetime_naive: datetime
    timezone_name: str
    resolved_utc_datetime: datetime
    fold: int
    utc_offset_minutes: int
    latitude: float
    longitude: float
    place_name: str
    tzdata_version: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class NewNatalChart:
    id: uuid.UUID
    birth_profile_id: uuid.UUID
    calculator: str
    calculator_version: str
    wrapper_version: str
    house_system: str
    house_placement_method: str
    zodiac_type: str
    calculation_flags: int
    input_hash: str
    result_json: dict[str, object]
    calculated_at: datetime


@dataclass(frozen=True, slots=True)
class StoredNatalChart:
    id: uuid.UUID
    birth_profile_id: uuid.UUID
    input_hash: str
    result_json: dict[str, object]


@dataclass(frozen=True, slots=True)
class NatalChartOutcome:
    chart_id: uuid.UUID
    profile_id: uuid.UUID
    input_hash: str
    status: Literal["calculated", "cached"]
    result: dict[str, object]
