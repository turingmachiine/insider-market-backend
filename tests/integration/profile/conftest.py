"""Profile service integration fixtures."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from dishka import Scope, make_async_container, provide
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from src.common.application.security import encode_jwt
from src.common.domain.security import Permission
from src.profile_service.core.config import ProfileSettings, settings
from src.profile_service.infrastructure.db import setup_mapping
from src.profile_service.infrastructure.db.metadata import mapper_registry
from src.profile_service.infrastructure.di.providers import (
    DatabaseProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)
from src.profile_service.main import create_app


class TestDatabaseProvider(DatabaseProvider):
    """Database provider backed by a test-owned engine."""

    scope = Scope.APP

    def __init__(
        self,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession],
        settings: ProfileSettings,
    ) -> None:
        super().__init__(settings=settings)
        self.engine = engine
        self.session_factory = session_factory

    @provide
    def provide_engine(self) -> AsyncEngine:
        return self.engine

    @provide
    def provide_session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self.session_factory

    @provide(scope=Scope.REQUEST)
    async def provide_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


@pytest.fixture(scope="session", autouse=True)
def setup_entity_mapping() -> None:
    setup_mapping()


@pytest.fixture(scope="session")
def profile_postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="function")
async def profile_db_engine(
    profile_postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    db_url = profile_postgres_container.get_connection_url().replace(
        "postgresql://",
        "postgresql+asyncpg://",
    )

    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.execute(text("DROP TYPE IF EXISTS profile_activity_type CASCADE"))
        await conn.execute(
            text("DROP TYPE IF EXISTS profile_balance_transaction_type CASCADE")
        )
        await conn.execute(
            text(
                "CREATE TYPE profile_activity_type AS ENUM "
                "('profile_created', 'profile_updated', 'balance_changed', "
                "'achievement_awarded', 'market_bet_placed', 'market_resolved')"
            )
        )
        await conn.execute(
            text(
                "CREATE TYPE profile_balance_transaction_type AS ENUM "
                "('credit', 'debit', 'reserve', 'release')"
            )
        )
        await conn.run_sync(mapper_registry.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def profile_test_container(profile_db_engine: AsyncEngine):
    session_factory = async_sessionmaker(
        profile_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    container = make_async_container(
        TestDatabaseProvider(profile_db_engine, session_factory, settings),
        RepositoryProvider(),
        MapperProvider(),
        UseCaseProvider(),
    )

    yield container
    await container.close()


@pytest_asyncio.fixture(scope="function")
async def profile_client(profile_test_container):
    app = create_app(container=profile_test_container)
    token = encode_jwt(
        {
            "sub": str(uuid4()),
            "permissions": [permission.value for permission in Permission],
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        },
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client
