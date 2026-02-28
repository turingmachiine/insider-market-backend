from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    # App
    APP_NAME: str = "Football Research API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "football_db"
    DATABASE_URL: PostgresDsn | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v

        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER", "postgres"),
            password=data.get("POSTGRES_PASSWORD", "postgres"),
            host=data.get("POSTGRES_HOST", "localhost"),
            port=data.get("POSTGRES_PORT", 5432),
            path=f"{data.get('POSTGRES_DB') or ''}",
        ).unicode_string()

    # External APIs
    FBREF_BASE_URL: str = "https://fbref.com"
    TRANSFERMARKT_BASE_URL: str = "https://transfermarkt.com"
    UNDERSTAT_BASE_URL: str = "https://understat.com"

    # API Keys
    RAPIDAPI_KEY: str | None = None
    FOOTBALL_DATA_API_KEY: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True

    # Cache
    REDIS_URL: str | None = None
    CACHE_TTL: int = 3600


settings = Settings()
