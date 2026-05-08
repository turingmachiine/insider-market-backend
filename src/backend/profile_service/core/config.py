from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProfileSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROXY_NAME: str = "profile"
    APP_NAME: str = "Football Research Profile Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PROFILE_PORT: int = 8007

    POSTGRES_USER_PROFILE: str = "postgres"
    POSTGRES_PASSWORD_PROFILE: str = "postgres"
    POSTGRES_HOST_PROFILE: str = "localhost"
    POSTGRES_PORT_PROFILE: int = 5437
    POSTGRES_DB_PROFILE: str = "profile_db"
    DATABASE_URL_PROFILE: PostgresDsn | None = None

    REDIS_URL: str | None = None

    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    LOG_BROKER_ENABLED: bool = False
    LOG_REDIS_URL: str | None = None
    LOG_REDIS_KEY: str = "logs:football"

    @field_validator("DATABASE_URL_PROFILE", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v

        data = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER_PROFILE", "postgres"),
            password=data.get("POSTGRES_PASSWORD_PROFILE", "postgres"),
            host=data.get("POSTGRES_HOST_PROFILE", "localhost"),
            port=data.get("POSTGRES_PORT_PROFILE", 5437),
            path=f"{data.get('POSTGRES_DB_PROFILE') or ''}",
        ).unicode_string()


settings = ProfileSettings()
