"""Market service integration fixtures."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timedelta
from uuid import UUID

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
from src.market_service.core.config import MarketSettings, settings
from src.market_service.infrastructure.db import setup_mapping
from src.market_service.infrastructure.db.metadata import mapper_registry
from src.market_service.infrastructure.di.providers import (
    DatabaseProvider,
    DomainServiceProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)
from src.market_service.main import create_app


class TestDatabaseProvider(DatabaseProvider):
    """Database provider backed by a test-owned engine."""

    scope = Scope.APP

    def __init__(
        self,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession],
        settings: MarketSettings,
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
def market_postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture(scope="function")
async def market_db_engine(
    market_postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    db_url = market_postgres_container.get_connection_url().replace(
        "postgresql://",
        "postgresql+asyncpg://",
    )

    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.execute(text("DROP TYPE IF EXISTS market_side CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS market_outcome CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS market_status CASCADE"))
        await conn.execute(
            text(
                "CREATE TYPE market_status AS ENUM "
                "('draft', 'active', 'paused', 'closed', 'resolved', 'cancelled')"
            )
        )
        await conn.execute(
            text("CREATE TYPE market_outcome AS ENUM ('yes', 'no', 'void')")
        )
        await conn.execute(text("CREATE TYPE market_side AS ENUM ('yes', 'no')"))
        await conn.run_sync(mapper_registry.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def market_test_container(market_db_engine: AsyncEngine):
    session_factory = async_sessionmaker(
        market_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    container = make_async_container(
        TestDatabaseProvider(market_db_engine, session_factory, settings),
        RepositoryProvider(),
        MapperProvider(),
        DomainServiceProvider(),
        UseCaseProvider(),
    )

    yield container
    await container.close()


@pytest_asyncio.fixture(scope="function")
async def market_client(
    market_test_container,
    authenticated_user_id: UUID,
):
    app = create_app(container=market_test_container)
    token = encode_jwt(
        {
            "sub": str(authenticated_user_id),
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
