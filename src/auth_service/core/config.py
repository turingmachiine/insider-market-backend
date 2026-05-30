from pydantic import AnyHttpUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.auth_service.application.constants import (
    DEFAULT_LOGIN_LOCKOUT_SECONDS,
    DEFAULT_MAX_FAILED_LOGIN_ATTEMPTS,
    DEFAULT_PASSWORD_RESET_TOKEN_TTL,
)


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "auth"
    APP_NAME: str = "Инсайдер Маркет Auth Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    AUTH_PORT: int = 8001

    POSTGRES_USER_AUTH: str = "postgres"
    POSTGRES_PASSWORD_AUTH: str = "postgres"
    POSTGRES_HOST_AUTH: str = "localhost"
    POSTGRES_PORT_AUTH: int = 5433
    POSTGRES_DB_AUTH: str = "auth_db"
    DATABASE_URL_AUTH: PostgresDsn | None = None

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_TTL: int = 3600
    REFRESH_TOKEN_TTL: int = 2_592_000
    PASSWORD_RESET_TOKEN_TTL: int = DEFAULT_PASSWORD_RESET_TOKEN_TTL
    MAX_FAILED_LOGIN_ATTEMPTS: int = DEFAULT_MAX_FAILED_LOGIN_ATTEMPTS
    LOGIN_LOCKOUT_SECONDS: int = DEFAULT_LOGIN_LOCKOUT_SECONDS

    REDIS_URL: str | None = None
    PERMISSIONS_CACHE_TTL: int = 300
    PROFILE_SERVICE_URL: AnyHttpUrl = AnyHttpUrl(url="http://profile_service:8007")
    MARKET_SERVICE_URL: AnyHttpUrl = AnyHttpUrl(url="http://market_service:8005")
    USER_PROVISIONING_ENABLED: bool = True
    PROVISIONING_REQUEST_TIMEOUT_SECONDS: float = 5.0
    SERVICE_NAME: str = "auth_service"
    SERVICE_JWT_SECRET: str = "change-me-service"
    SERVICE_JWT_ALGORITHM: str = "HS256"
    SERVICE_JWT_TTL: int = 300

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    @field_validator("DATABASE_URL_AUTH", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v

        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER_AUTH", "postgres"),
            password=data.get("POSTGRES_PASSWORD_AUTH", "postgres"),
            host=data.get("POSTGRES_HOST_AUTH", "localhost"),
            port=data.get("POSTGRES_PORT_AUTH", 5433),
            path=f"{data.get('POSTGRES_DB_AUTH') or ''}",
        ).unicode_string()


settings = AuthSettings()
