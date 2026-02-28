"""Fixtures для интеграционных тестов с testcontainers"""

from datetime import date
from decimal import Decimal
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from src.domain.entities.club import Club
from src.domain.entities.league import League
from src.domain.entities.player import Player
from src.domain.entities.team import Team
from src.domain.value_objects.position import Position
from src.infrastructure.db import setup_mapping
from src.infrastructure.db.metadata import mapper_registry
from src.infrastructure.db.repositories import (
    ClubRepository,
    LeagueRepository,
    PlayerRepository,
    TeamRepository,
)


@pytest.fixture(scope="session", autouse=True)
def setup_entity_mapping() -> None:
    """Настроить маппинг Entity один раз для всех интеграционных тестов"""
    setup_mapping()


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Создать PostgreSQL контейнер для тестов"""
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, None, None]:
    """Создать Redis контейнер для тестов"""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="function")
async def db_engine(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    """Создать движок БД для тестов"""
    db_url = postgres_container.get_connection_url()
    # Заменяем синхронный драйвер на асинхронный
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
    )

    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)

    yield engine

    # Очистка
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Создать сессию БД для тестов"""
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


# =============================================================================
# Фикстуры репозиториев
# =============================================================================


@pytest.fixture
async def player_repository(
    db_session: AsyncSession,
) -> PlayerRepository:
    """Репозиторий игроков для тестов"""
    return PlayerRepository(db_session)


@pytest.fixture
async def club_repository(
    db_session: AsyncSession,
) -> ClubRepository:
    """Репозиторий клубов для тестов"""
    return ClubRepository(db_session)


@pytest.fixture
async def league_repository(
    db_session: AsyncSession,
) -> LeagueRepository:
    """Репозиторий лиг для тестов"""
    return LeagueRepository(db_session)


@pytest.fixture
async def team_repository(
    db_session: AsyncSession,
) -> TeamRepository:
    """Репозиторий команд для тестов"""
    return TeamRepository(db_session)


@pytest.fixture
def sample_league_entity() -> League:
    """Создать тестовую лигу"""
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
    """Создать тестовый клуб"""
    # Не устанавливаем league_id чтобы избежать FK проблем в тестах
    return Club(
        id=uuid4(),
        name="Manchester City",
        short_name="Man City",
        founded_year=1880,
        country="England",
        city="Manchester",
        stadium_name="Etihad Stadium",
        stadium_capacity=55000,
        league_id=None,  # FK может отсутствовать
        logo_url="https://example.com/mancity.png",
        website="https://mancity.com",
        squad_market_value=Decimal("1000000000"),
        average_age=26.5,
        foreign_players_count=20,
        national_team_players_count=15,
    )


@pytest.fixture
def sample_player_entity(sample_league_entity: League) -> Player:
    """Создать тестового игрока"""
    # Не устанавливаем current_club_id чтобы избежать FK проблем в тестах
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
        current_club_id=None,  # FK может отсутствовать
        current_league_id=None,  # FK может отсутствовать
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
    """Создать тестовую команду"""
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
