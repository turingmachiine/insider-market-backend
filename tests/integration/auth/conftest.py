"""Auth service API fixtures."""

from collections.abc import AsyncGenerator, Generator
from typing import Any, cast

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.auth_service.application.service import AuthService
from src.auth_service.core.config import settings
from src.auth_service.infrastructure.db.metadata import Base
from src.auth_service.infrastructure.di import create_container
from src.auth_service.main import create_app


class AuthTestSettings:
    """Applies and restores mutable auth settings for integration tests."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.original_database_url = settings.DATABASE_URL_AUTH
        self.original_redis_url = settings.REDIS_URL
        self.original_jwt_secret = settings.JWT_SECRET
        self.original_jwt_ttl = settings.JWT_TTL
        self.original_refresh_token_ttl = settings.REFRESH_TOKEN_TTL
        self.original_password_reset_token_ttl = settings.PASSWORD_RESET_TOKEN_TTL
        self.original_max_failed_login_attempts = settings.MAX_FAILED_LOGIN_ATTEMPTS
        self.original_login_lockout_seconds = settings.LOGIN_LOCKOUT_SECONDS

    def apply(self) -> None:
        settings.DATABASE_URL_AUTH = cast(Any, self.database_url)
        settings.REDIS_URL = None
        settings.JWT_SECRET = "test-secret"
        settings.JWT_TTL = 3600
        settings.REFRESH_TOKEN_TTL = 3600
        settings.PASSWORD_RESET_TOKEN_TTL = 3600
        settings.MAX_FAILED_LOGIN_ATTEMPTS = 5
        settings.LOGIN_LOCKOUT_SECONDS = 900

    def restore(self) -> None:
        settings.DATABASE_URL_AUTH = self.original_database_url
        settings.REDIS_URL = self.original_redis_url
        settings.JWT_SECRET = self.original_jwt_secret
        settings.JWT_TTL = self.original_jwt_ttl
        settings.REFRESH_TOKEN_TTL = self.original_refresh_token_ttl
        settings.PASSWORD_RESET_TOKEN_TTL = self.original_password_reset_token_ttl
        settings.MAX_FAILED_LOGIN_ATTEMPTS = self.original_max_failed_login_attempts
        settings.LOGIN_LOCKOUT_SECONDS = self.original_login_lockout_seconds


@pytest.fixture
def auth_postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture
async def auth_engine(
    auth_postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    db_url = auth_postgres_container.get_connection_url().replace(
        "postgresql://",
        "postgresql+asyncpg://",
    )
    test_settings = AuthTestSettings(db_url)
    test_settings.apply()

    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    test_settings.restore()


@pytest.fixture
async def auth_client(auth_engine: AsyncEngine):
    container = create_container(settings)
    async with container() as request_container:
        auth_service = await request_container.get(AuthService)
        await auth_service.bootstrap_access_control()

    app = create_app(container=container)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    await container.close()
