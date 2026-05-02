from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "auth"
    APP_NAME: str = "Football Research Auth Service"
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

    REDIS_URL: str | None = None
    PERMISSIONS_CACHE_TTL: int = 300

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
