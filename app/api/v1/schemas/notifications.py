import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FirebaseInstallationCreate(BaseModel):
    fid: str = Field(min_length=10, max_length=255)
    platform: str = Field(default="android", pattern="^(android)$")


class FirebaseInstallationResponse(BaseModel):
    id: uuid.UUID
    fid: str
    platform: str
    updated_at: datetime
