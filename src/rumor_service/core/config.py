from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RumorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "rumor"
    APP_NAME: str = "Инсайдер Маркет Rumor Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    RUMOR_PORT: int = 8003

    POSTGRES_USER_RUMOR: str = "postgres"
    POSTGRES_PASSWORD_RUMOR: str = "postgres"
    POSTGRES_HOST_RUMOR: str = "localhost"
    POSTGRES_PORT_RUMOR: int = 5434
    POSTGRES_DB_RUMOR: str = "rumor_db"
    DATABASE_URL_RUMOR: PostgresDsn | None = None

    REDIS_URL: str | None = None
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    SERVICE_NAME: str = "rumor_service"
    SERVICE_JWT_SECRET: str = "change-me-service"
    SERVICE_JWT_ALGORITHM: str = "HS256"
    SERVICE_JWT_TTL: int = 300

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    @field_validator("DATABASE_URL_RUMOR", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v

        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER_RUMOR", "postgres"),
            password=data.get("POSTGRES_PASSWORD_RUMOR", "postgres"),
            host=data.get("POSTGRES_HOST_RUMOR", "localhost"),
            port=data.get("POSTGRES_PORT_RUMOR", 5434),
            path=f"{data.get('POSTGRES_DB_RUMOR') or ''}",
        ).unicode_string()


settings = RumorSettings()
