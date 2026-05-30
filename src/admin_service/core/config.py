from functools import lru_cache

from pydantic import AnyHttpUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "admin"
    APP_NAME: str = "Инсайдер Маркет Admin Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    ADMIN_PORT: int = 8009

    POSTGRES_USER_ADMIN: str = "postgres"
    POSTGRES_PASSWORD_ADMIN: str = "postgres"
    POSTGRES_HOST_ADMIN: str = "localhost"
    POSTGRES_PORT_ADMIN: int = 5439
    POSTGRES_DB_ADMIN: str = "admin_db"
    DATABASE_URL_ADMIN: PostgresDsn | None = None

    SERVICE_AUTH_URL: AnyHttpUrl = AnyHttpUrl(url="http://auth_service:8002")
    SERVICE_EVENT_URL: AnyHttpUrl = AnyHttpUrl(url="http://event_service:8004")
    SERVICE_PROFILE_URL: AnyHttpUrl = AnyHttpUrl(url="http://profile_service:8007")
    SERVICE_RATING_URL: AnyHttpUrl = AnyHttpUrl(url="http://rating_service:8008")
    SERVICE_MARKET_URL: AnyHttpUrl = AnyHttpUrl(url="http://market_service:8005")
    SERVICE_RUMOR_URL: AnyHttpUrl = AnyHttpUrl(url="http://rumor_service:8003")
    SERVICE_NSI_URL: AnyHttpUrl = AnyHttpUrl(url="http://nsi_service:8001")

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    REDIS_URL: str | None = None
    ADMIN_CLIENT_TIMEOUT_SECONDS: float = 10.0
    DASHBOARD_PREVIEW_LIMIT: int = 10

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    @field_validator("DATABASE_URL_ADMIN", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER_ADMIN", "postgres"),
            password=data.get("POSTGRES_PASSWORD_ADMIN", "postgres"),
            host=data.get("POSTGRES_HOST_ADMIN", "localhost"),
            port=data.get("POSTGRES_PORT_ADMIN", 5439),
            path=f"{data.get('POSTGRES_DB_ADMIN') or ''}",
        ).unicode_string()


@lru_cache
def get_settings() -> AdminSettings:
    return AdminSettings()


settings = get_settings()
