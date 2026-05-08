from functools import lru_cache

from pydantic import AnyHttpUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RatingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "rating"
    APP_NAME: str = "Football Research Rating Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    RATING_PORT: int = 8008

    POSTGRES_USER_RATING: str = "postgres"
    POSTGRES_PASSWORD_RATING: str = "postgres"
    POSTGRES_HOST_RATING: str = "localhost"
    POSTGRES_PORT_RATING: int = 5438
    POSTGRES_DB_RATING: str = "rating_db"
    DATABASE_URL_RATING: PostgresDsn | None = None

    PROFILE_SERVICE_URL: AnyHttpUrl = AnyHttpUrl(url="http://profile_service:8007")
    REWARD_REQUEST_TIMEOUT_SECONDS: float = 5.0

    REDIS_URL: str | None = "redis://redis:6379/0"
    TASKIQ_REDIS_URL: str = "redis://redis:6379/0"
    TASKIQ_QUEUE_NAME: str = "football_research_rating"
    RATING_EVENTS_CRON: str = "*/5 * * * *"
    RATING_REWARDS_CRON: str = "*/2 * * * *"
    BACKGROUND_BATCH_SIZE: int = 250

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    @field_validator("DATABASE_URL_RATING", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER_RATING", "postgres"),
            password=data.get("POSTGRES_PASSWORD_RATING", "postgres"),
            host=data.get("POSTGRES_HOST_RATING", "localhost"),
            port=data.get("POSTGRES_PORT_RATING", 5438),
            path=f"{data.get('POSTGRES_DB_RATING') or ''}",
        ).unicode_string()


@lru_cache
def get_settings() -> RatingSettings:
    return RatingSettings()


settings = get_settings()
