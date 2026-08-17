import uuid

from pydantic import BaseModel, Field, field_validator


class UserReportCreate(BaseModel):
    reported_user_id: uuid.UUID
    message_id: uuid.UUID | None = None
    reason: str = Field(pattern=r"^(spam|harassment|inappropriate|other)$")
    details: str | None = Field(default=None, max_length=500)

    @field_validator("details")
    @classmethod
    def clean_details(cls, value: str | None) -> str | None:
        cleaned = value.strip() if value else ""
        return cleaned or None


class AthenaFeedbackCreate(BaseModel):
    content_type: str = Field(pattern=r"^(natal|daily_sign|daily_premium)$")
    reason: str = Field(pattern=r"^(unsafe|incorrect|offensive|other)$")
    details: str | None = Field(default=None, max_length=500)

    @field_validator("details")
    @classmethod
    def clean_details(cls, value: str | None) -> str | None:
        cleaned = value.strip() if value else ""
        return cleaned or None


class ProductFeedbackCreate(BaseModel):
    category: str = Field(pattern=r"^(idea|bug|experience)$")
    rating: int = Field(ge=1, le=5)
    details: str = Field(min_length=10, max_length=1000)

    @field_validator("details")
    @classmethod
    def clean_product_details(cls, value: str) -> str:
        return value.strip()


class ModerationActionResponse(BaseModel):
    status: str
