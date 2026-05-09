"""Rating service integration fixtures."""

from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from src.rating_service.application.ports import ProfileBalancePort
from src.rating_service.core.config import RatingSettings
from src.rating_service.infrastructure.db import setup_mapping
from src.rating_service.infrastructure.db.metadata import mapper_registry
from src.rating_service.infrastructure.di.providers import (
    DatabaseProvider,
    DomainServiceProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)
from src.rating_service.main import create_app


class TestDatabaseProvider(DatabaseProvider):
    scope = Scope.APP

    def __init__(
        self,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession],
        settings: RatingSettings,
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


class FakeProfileBalancePort(ProfileBalancePort):
    async def credit_achievement_reward(self, *args, **kwargs) -> None:
        return None


class TestClientProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_profile_balance_port() -> ProfileBalancePort:
        return FakeProfileBalancePort()


@pytest.fixture(scope="session", autouse=True)
def setup_entity_mapping() -> None:
    setup_mapping()


@pytest.fixture(scope="session")
def rating_postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="function")
async def rating_db_engine(
    rating_postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    db_url = rating_postgres_container.get_connection_url().replace(
        "postgresql://",
        "postgresql+asyncpg://",
    )
    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.execute(text("DROP TYPE IF EXISTS rating_user_status CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS rating_event_type CASCADE"))
        await conn.execute(
            text("DROP TYPE IF EXISTS rating_achievement_rarity CASCADE")
        )
        await conn.execute(
            text("DROP TYPE IF EXISTS rating_reward_transaction_status CASCADE")
        )
        await conn.execute(
            text(
                "CREATE TYPE rating_user_status AS ENUM "
                "('rookie', 'scout', 'analyst', 'expert', 'legend')"
            )
        )
        await conn.execute(
            text(
                "CREATE TYPE rating_event_type AS ENUM "
                "('prediction_settled', 'market_created', 'analysis_published', "
                "'daily_active', 'comment_posted')"
            )
        )
        await conn.execute(
            text(
                "CREATE TYPE rating_achievement_rarity AS ENUM "
                "('common', 'rare', 'epic', 'legendary')"
            )
        )
        await conn.execute(
            text(
                "CREATE TYPE rating_reward_transaction_status AS ENUM "
                "('pending', 'sent', 'failed')"
            )
        )
        await conn.run_sync(mapper_registry.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def rating_test_container(rating_db_engine: AsyncEngine):
    session_factory = async_sessionmaker(
        rating_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    settings = RatingSettings.model_validate(
        {
            "DATABASE_URL_RATING": (
                "postgresql+asyncpg://postgres:postgres@localhost/test"
            )
        }
    )
    container = make_async_container(
        TestDatabaseProvider(rating_db_engine, session_factory, settings),
        TestClientProvider(),
        RepositoryProvider(),
        DomainServiceProvider(),
        MapperProvider(),
        UseCaseProvider(),
    )

    yield container
    await container.close()


@pytest_asyncio.fixture(scope="function")
async def rating_client(rating_test_container):
    app = create_app(container=rating_test_container)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
