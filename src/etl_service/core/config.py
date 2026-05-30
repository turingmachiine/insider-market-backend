from pydantic_settings import BaseSettings, SettingsConfigDict


class ETLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Инсайдер Маркет ETL Service"
    APP_VERSION: str = "0.1.0"
    RUMOR_SERVICE_URL: str = "http://rumor_service:8003"
    TASKIQ_REDIS_URL: str = "redis://redis:6379/0"
    TASKIQ_QUEUE_NAME: str = "insider_market_backend_etl"
    REQUEST_TIMEOUT_SECONDS: float = 20.0
    SOURCE_FETCH_LIMIT: int = 20
    RAW_PUBLICATIONS_LIMIT: int = 500
    EXISTING_RUMORS_LIMIT: int = 500
    RAW_IMPORT_CRON: str = "*/30 * * * *"
    RUMOR_NORMALIZATION_CRON: str = "*/15 * * * *"
    SERVICE_NAME: str = "etl_service"
    SERVICE_JWT_SECRET: str = "change-me-service"
    SERVICE_JWT_ALGORITHM: str = "HS256"
    SERVICE_JWT_TTL: int = 300


def get_settings() -> ETLSettings:
    return ETLSettings()
