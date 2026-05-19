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

    APP_NAME: str = "Football Research Insider Market Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = 8000

    SERVICE_NSI_URL: AnyHttpUrl = AnyHttpUrl(url="http://nsi_service:8001")
    SERVICE_AUTH_URL: AnyHttpUrl = AnyHttpUrl(url="http://auth_service:8002")
    SERVICE_RUMOR_URL: AnyHttpUrl = AnyHttpUrl(url="http://rumor_service:8003")
    SERVICE_EVENT_URL: AnyHttpUrl = AnyHttpUrl(url="http://event_service:8004")
    SERVICE_MARKET_URL: AnyHttpUrl = AnyHttpUrl(url="http://market_service:8005")
    SERVICE_NOTIFICATION_URL: AnyHttpUrl = AnyHttpUrl(
        url="http://notification_service:8006"
    )
    SERVICE_PROFILE_URL: AnyHttpUrl = AnyHttpUrl(url="http://profile_service:8007")
    SERVICE_RATING_URL: AnyHttpUrl = AnyHttpUrl(url="http://rating_service:8008")
    SERVICE_ADMIN_URL: AnyHttpUrl = AnyHttpUrl(url="http://admin_service:8009")
    REDIS_URL: str = "redis://redis:6379/0"

    RATE_LIMIT: str = "100/minute"
    PUBLIC_RATE_LIMIT: str | None = None
    SENSITIVE_RATE_LIMIT: str = "10/minute"
    WEBSOCKET_RATE_LIMIT: str = "20/minute"
    RATE_LIMIT_BY_JWT: bool = True
    CACHE_TTL_SECONDS: int = 30
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
        ]
    )
    CORS_METHODS: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    CORS_HEADERS: list[str] = Field(
        default_factory=lambda: [
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-Service-Authorization",
        ]
    )
    CORS_EXPOSE_HEADERS: list[str] = Field(
        default_factory=lambda: ["X-Request-ID", "Retry-After"]
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    MAX_BODY_SIZE_MB: int = 10
    HSTS_MAX_AGE_SECONDS: int = 31_536_000
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = False
    CONTENT_SECURITY_POLICY: str = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "img-src 'self' data:; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "connect-src 'self'"
    )
    X_FRAME_OPTIONS: str = "DENY"
    REFERRER_POLICY: str = "no-referrer"
    PERMISSIONS_POLICY: str = (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    )

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

    @field_validator(
        "RATE_LIMIT",
        "PUBLIC_RATE_LIMIT",
        "SENSITIVE_RATE_LIMIT",
        "WEBSOCKET_RATE_LIMIT",
    )
    @classmethod
    def validate_rate_limit(cls, value: str | None) -> str | None:
        if value is None:
            return value
        limit, _, period = value.partition("/")
        if not limit.isdigit() or int(limit) <= 0:
            raise ValueError("Rate limit must be formatted as '<positive int>/minute'")
        if period != "minute":
            raise ValueError("Only minute rate limit period is supported")
        return value

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("CORS_ORIGINS must contain at least one explicit origin")
        if "*" in value:
            raise ValueError("CORS_ORIGINS must not use wildcard origins")
        return value

    @property
    def rate_limit_requests(self) -> int:
        return int(self.RATE_LIMIT.split("/", 1)[0])

    @property
    def public_rate_limit_requests(self) -> int:
        return int((self.PUBLIC_RATE_LIMIT or self.RATE_LIMIT).split("/", 1)[0])

    @property
    def sensitive_rate_limit_requests(self) -> int:
        return int(self.SENSITIVE_RATE_LIMIT.split("/", 1)[0])

    @property
    def websocket_rate_limit_requests(self) -> int:
        return int(self.WEBSOCKET_RATE_LIMIT.split("/", 1)[0])

    @property
    def max_body_size_bytes(self) -> int:
        return self.MAX_BODY_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> GatewaySettings:
    return GatewaySettings()
