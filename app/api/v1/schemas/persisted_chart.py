import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict


class NatalChartCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    house_system: Literal["P"] = "P"


class PersistedNatalChartResponse(BaseModel):
    schema_version: str
    chart_id: uuid.UUID
    profile_id: uuid.UUID
    input_hash: str
    status: Literal["calculated", "cached"]
    result: dict[str, object]
