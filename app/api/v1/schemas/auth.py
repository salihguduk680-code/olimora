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
        if (
            len(value) < 10
            or not any(char.isalpha() for char in value)
            or not any(char.isdigit() for char in value)
        ):
            raise ValueError("şifre en az 10 karakter, bir harf ve bir rakam içermeli")
        return value


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if not any(char.isalpha() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("yeni şifre en az bir harf ve bir rakam içermeli")
        return value


class EmailRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)

    @field_validator("email")
    @classmethod
    def validate_request_email(cls, value: str) -> str:
        return CredentialsRequest.validate_email(value)


class TokenRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class PasswordResetRequest(TokenRequest):
    new_password: str = Field(min_length=10, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_reset_password(cls, value: str) -> str:
        return PasswordChangeRequest.validate_new_password(value)


class ActionResponse(BaseModel):
    status: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime
    email_verified: bool = False


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
