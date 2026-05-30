from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MarketSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "market"
    APP_NAME: str = "Инсайдер Маркет Market Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    MARKET_PORT: int = 8005

    POSTGRES_USER_MARKET: str = "postgres"
    POSTGRES_PASSWORD_MARKET: str = "postgres"
    POSTGRES_HOST_MARKET: str = "localhost"
    POSTGRES_PORT_MARKET: int = 5436
    POSTGRES_DB_MARKET: str = "market_db"
    DATABASE_URL_MARKET: PostgresDsn | None = None

    REDIS_URL: str | None = None
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    SERVICE_NAME: str = "market_service"
    SERVICE_JWT_SECRET: str = "change-me-service"
    SERVICE_JWT_ALGORITHM: str = "HS256"
    SERVICE_JWT_TTL: int = 300

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    @field_validator("DATABASE_URL_MARKET", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v

        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER_MARKET", "postgres"),
            password=data.get("POSTGRES_PASSWORD_MARKET", "postgres"),
            host=data.get("POSTGRES_HOST_MARKET", "localhost"),
            port=data.get("POSTGRES_PORT_MARKET", 5436),
            path=f"{data.get('POSTGRES_DB_MARKET') or ''}",
        ).unicode_string()


settings = MarketSettings()
