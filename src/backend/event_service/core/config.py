from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EventSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "event"
    APP_NAME: str = "Football Research Event Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    EVENT_PORT: int = 8004

    POSTGRES_USER_EVENT: str = "postgres"
    POSTGRES_PASSWORD_EVENT: str = "postgres"
    POSTGRES_HOST_EVENT: str = "localhost"
    POSTGRES_PORT_EVENT: int = 5435
    POSTGRES_DB_EVENT: str = "event_db"
    DATABASE_URL_EVENT: PostgresDsn | None = None

    REDIS_URL: str | None = None

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    @field_validator("DATABASE_URL_EVENT", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v

        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER_EVENT", "postgres"),
            password=data.get("POSTGRES_PASSWORD_EVENT", "postgres"),
            host=data.get("POSTGRES_HOST_EVENT", "localhost"),
            port=data.get("POSTGRES_PORT_EVENT", 5435),
            path=f"{data.get('POSTGRES_DB_EVENT') or ''}",
        ).unicode_string()


settings = EventSettings()
