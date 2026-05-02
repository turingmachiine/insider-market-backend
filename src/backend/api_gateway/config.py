from functools import lru_cache

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Football Research API Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = 8000

    SERVICE_NSI_URL: AnyHttpUrl = AnyHttpUrl(url="http://nsi_service:8001")
    SERVICE_AUTH_URL: AnyHttpUrl = AnyHttpUrl(url="http://auth_service:8002")
    REDIS_URL: str = "redis://redis:6379/0"

    RATE_LIMIT: str = "100/minute"
    RATE_LIMIT_BY_JWT: bool = True
    CACHE_TTL_SECONDS: int = 30
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    MAX_BODY_SIZE_MB: int = 10

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    SERVICE_TIMEOUT_SECONDS: float = 5.0
    TOTAL_TIMEOUT_SECONDS: float = 10.0
    STATS_TTL_SECONDS: int = 300

    @field_validator("RATE_LIMIT")
    @classmethod
    def validate_rate_limit(cls, value: str) -> str:
        limit, _, period = value.partition("/")
        if not limit.isdigit() or int(limit) <= 0:
            raise ValueError("RATE_LIMIT must be formatted as '<positive int>/minute'")
        if period != "minute":
            raise ValueError("Only minute rate limit period is supported")
        return value

    @property
    def rate_limit_requests(self) -> int:
        return int(self.RATE_LIMIT.split("/", 1)[0])

    @property
    def max_body_size_bytes(self) -> int:
        return self.MAX_BODY_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> GatewaySettings:
    return GatewaySettings()
