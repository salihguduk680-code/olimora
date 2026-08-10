from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://olimora:olimora-local-dev@localhost:5432/olimora"
    app_env: str = "development"
    log_level: str = "INFO"
    ephemeris_path: str = "ephe"
    app_version: str = "0.1.0"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"
    openai_timeout_seconds: float = 20.0
    athena_max_output_tokens: int = 500
    athena_requests_per_minute: int = 5
    auth_secret: str = "olimora-local-development-secret-change-me"
    auth_token_days: int = 30
    firebase_project_id: str | None = None
    firebase_service_account_json: str | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        return value

    @model_validator(mode="after")
    def require_private_auth_secret_in_production(self) -> "Settings":
        if self.app_env == "production" and "local-development" in self.auth_secret:
            raise ValueError("AUTH_SECRET must be configured in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
