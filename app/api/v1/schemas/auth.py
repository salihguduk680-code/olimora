import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CredentialsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.count("@") != 1 or "." not in normalized.rsplit("@", 1)[1]:
            raise ValueError("geçerli bir e-posta adresi olmalı")
        return normalized


class RegistrationRequest(CredentialsRequest):
    @field_validator("password")
    @classmethod
    def validate_registration_password(cls, value: str) -> str:
        if len(value) < 10 or not any(char.isalpha() for char in value) or not any(
            char.isdigit() for char in value
        ):
            raise ValueError("şifre en az 10 karakter, bir harf ve bir rakam içermeli")
        return value


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
