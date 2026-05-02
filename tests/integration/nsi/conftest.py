"""NSI integration fixtures."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from dishka import Scope, make_async_container, provide
from jose import jwt
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from src.backend.nsi_service.core.config import Settings, settings
from src.backend.nsi_service.domain.entities.club import Club
from src.backend.nsi_service.domain.entities.league import League
from src.backend.nsi_service.domain.entities.player import Player
from src.backend.nsi_service.domain.entities.team import Team
from src.backend.nsi_service.domain.value_objects.position import Position
from src.backend.nsi_service.infrastructure.db import setup_mapping
from src.backend.nsi_service.infrastructure.db.metadata import mapper_registry
from src.backend.nsi_service.infrastructure.db.repositories import (
    ClubRepository,
    LeagueRepository,
    PlayerRepository,
    TeamRepository,
)
from src.backend.nsi_service.infrastructure.di.providers import (
    ContainerProvider,
    DatabaseProvider,
    DomainServiceProvider,
    MapperProvider,
    ProcessingProvider,
    RepositoryProvider,
    UseCaseProvider,
)
from src.backend.nsi_service.main import create_app


class TestDatabaseProvider(DatabaseProvider):
    """Database provider backed by a test-owned engine."""

    scope = Scope.APP

    def __init__(
        self,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession],
        settings: Settings,
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
    """Configure imperative SQLAlchemy mapping once per test session."""
    setup_mapping()


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """PostgreSQL container used by NSI integration tests."""
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture(scope="function")
async def db_engine(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    """Create a fresh SQLAlchemy engine and schema for a test."""
    db_url = postgres_container.get_connection_url().replace(
        "postgresql://",
        "postgresql+asyncpg://",
    )

    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.run_sync(mapper_registry.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_engine(db_engine: AsyncEngine) -> AsyncEngine:
    """Alias for API tests that need a DI-backed engine."""
    return db_engine


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a rollback-only database session for repository tests."""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def player_repository(db_session: AsyncSession) -> PlayerRepository:
    return PlayerRepository(db_session)


@pytest.fixture
async def club_repository(db_session: AsyncSession) -> ClubRepository:
    return ClubRepository(db_session)


@pytest.fixture
async def league_repository(db_session: AsyncSession) -> LeagueRepository:
    return LeagueRepository(db_session)


@pytest.fixture
async def team_repository(db_session: AsyncSession) -> TeamRepository:
    return TeamRepository(db_session)


@pytest.fixture
def test_token() -> str:
    return jwt.encode(
        {
            "sub": str(uuid4()),
            "permissions": ["nsi:read", "team:write"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


@pytest_asyncio.fixture(scope="function")
async def test_container(test_db_engine: AsyncEngine):
    session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    container = make_async_container(
        TestDatabaseProvider(test_db_engine, session_factory, settings),
        RepositoryProvider(),
        DomainServiceProvider(),
        MapperProvider(),
        ProcessingProvider(),
        UseCaseProvider(),
        ContainerProvider(settings),
    )

    yield container
    await container.close()


@pytest_asyncio.fixture(scope="function")
async def api_client(test_container, test_token: str):
    app = create_app(container=test_container)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        client.headers.update({"Authorization": f"Bearer {test_token}"})
        yield client


@pytest.fixture
def sample_league_entity() -> League:
    return League(
        id=uuid4(),
        name="Premier League",
        short_name="EPL",
        country="England",
        tier=1,
        confederation="UEFA",
        logo_url="https://example.com/epl.png",
        strength_coefficient=1.0,
        current_season="2024/2025",
        season_start=date(2024, 8, 1),
        season_end=date(2025, 5, 31),
    )


@pytest.fixture
def sample_club_entity() -> Club:
    return Club(
        id=uuid4(),
        name="Manchester City",
        short_name="Man City",
        founded_year=1880,
        country="England",
        city="Manchester",
        stadium_name="Etihad Stadium",
        stadium_capacity=55000,
        league_id=None,
        logo_url="https://example.com/mancity.png",
        website="https://mancity.com",
        squad_market_value=Decimal("1000000000"),
        average_age=26.5,
        foreign_players_count=20,
        national_team_players_count=15,
    )


@pytest.fixture
def sample_player_entity(sample_league_entity: League) -> Player:
    return Player(
        id=uuid4(),
        name="Erling Haaland",
        first_name="Erling",
        last_name="Haaland",
        date_of_birth=date(2000, 7, 21),
        nationality="Norway",
        position=Position.ST,
        preferred_foot="left",
        height_cm=195,
        weight_kg=88,
        current_club_id=None,
        current_league_id=None,
        market_value=Decimal("180000000"),
        contract_until=date(2027, 6, 30),
        shirt_number=9,
        appearances=30,
        goals=25,
        assists=5,
        minutes_played=2500,
        xg=22.5,
        xa=4.2,
        xg_per_90=0.81,
        xa_per_90=0.15,
        league_strength_coefficient=1.0,
    )


@pytest.fixture
def sample_team_entity() -> Team:
    return Team(
        id=uuid4(),
        name="My Dream Team",
        user_id=uuid4(),
        description="Test team",
        squad={
            Position.GK.value: [str(uuid4())],
            Position.ST.value: [str(uuid4())],
        },
    )
