from datetime import UTC, datetime, timedelta
from typing import AsyncGenerator
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
from src.backend.nsi_service.infrastructure.db.metadata import mapper_registry
from src.backend.nsi_service.infrastructure.di.providers import (
    ContainerProvider,
    DatabaseProvider,
    DomainServiceProvider,
    MapperProvider,
    ProcessingProvider,
    RepositoryProvider,
    UseCaseProvider,
)


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


class TestDatabaseProvider(DatabaseProvider):
    """Провайдер базы данных для тестов"""

    scope = Scope.APP

    def __init__(
        self,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession],
        settings: Settings,
    ):
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


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    """Создать PostgreSQL контейнер для тестов"""
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture(scope="function")
async def test_db_engine(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    """Создать движок БД для тестов"""
    db_url = postgres_container.get_connection_url()
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
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_container(test_db_engine: AsyncEngine):
    """Создать DI контейнер для тестов"""
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
    # Закрываем контейнер в том же event loop
    await container.close()


@pytest_asyncio.fixture(scope="function")
async def api_client(test_container, test_token: str):
    """Создать асинхронный тестовый клиент API с DI"""
    from src.backend.nsi_service.main import create_app

    app = create_app(container=test_container)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        client.headers.update({"Authorization": f"Bearer {test_token}"})
        yield client


# =============================================================================
# Тесты
# =============================================================================


class TestPlayerAPI:
    """Интеграционные тесты Player API"""

    @pytest.mark.asyncio
    async def test_create_and_get_player(self, api_client: httpx.AsyncClient) -> None:
        """Тест создания и получения игрока"""
        player_data = {
            "name": "Test Player",
            "first_name": "Test",
            "last_name": "Player",
            "date_of_birth": "1995-05-15",
            "nationality": "England",
            "position": "striker",
            "preferred_foot": "right",
            "height_cm": 185,
            "weight_kg": 80,
            "market_value": "50000000",
            "shirt_number": 9,
        }

        # Создание
        response = await api_client.post("/api/v1/players", json=player_data)
        assert response.status_code == 201

        data = response.json()
        player_id = data["id"]

        assert data["name"] == "Test Player"
        assert data["position"] == "striker"
        assert data["height_cm"] == 185

        # Получение
        response = await api_client.get(f"/api/v1/players/{player_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == player_id
        assert data["name"] == "Test Player"

    @pytest.mark.asyncio
    async def test_search_players(self, api_client: httpx.AsyncClient) -> None:
        """Тест поиска игроков"""
        # Создаем игрока
        player_data = {
            "name": "John Smith",
            "date_of_birth": "1995-01-01",
            "nationality": "England",
            "position": "striker",
            "preferred_foot": "right",
            "height_cm": 180,
            "weight_kg": 75,
        }

        response = await api_client.post("/api/v1/players", json=player_data)
        assert response.status_code == 201

        # Поиск
        response = await api_client.get(
            "/api/v1/players/search", params={"name": "John"}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert any(p["name"] == "John Smith" for p in data)

    @pytest.mark.asyncio
    async def test_get_all_players(self, api_client: httpx.AsyncClient) -> None:
        """Тест получения списка игроков"""
        response = await api_client.get(
            "/api/v1/players", params={"limit": 10, "offset": 0}
        )
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

    @pytest.mark.asyncio
    async def test_get_player_not_found(self, api_client: httpx.AsyncClient) -> None:
        """Тест получения несуществующего игрока"""
        fake_id = str(uuid4())
        response = await api_client.get(f"/api/v1/players/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_player(self, api_client: httpx.AsyncClient) -> None:
        """Тест обновления игрока"""
        # Создаем
        player_data = {
            "name": "Update Me",
            "date_of_birth": "1995-01-01",
            "nationality": "England",
            "position": "striker",
            "preferred_foot": "right",
            "height_cm": 180,
            "weight_kg": 75,
        }

        response = await api_client.post("/api/v1/players", json=player_data)
        assert response.status_code == 201
        player_id = response.json()["id"]

        # Обновляем
        update_data = {
            "name": "Updated Name",
            "height_cm": 185,
        }

        response = await api_client.patch(
            f"/api/v1/players/{player_id}", json=update_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["height_cm"] == 185

    @pytest.mark.asyncio
    async def test_delete_player(self, api_client: httpx.AsyncClient) -> None:
        """Тест удаления игрока"""
        # Создаем
        player_data = {
            "name": "Delete Me",
            "date_of_birth": "1995-01-01",
            "nationality": "England",
            "position": "striker",
            "preferred_foot": "right",
            "height_cm": 180,
            "weight_kg": 75,
        }

        response = await api_client.post("/api/v1/players", json=player_data)
        assert response.status_code == 201
        player_id = response.json()["id"]

        # Удаляем
        response = await api_client.delete(f"/api/v1/players/{player_id}")
        assert response.status_code == 200

        # Проверяем что удален
        response = await api_client.get(f"/api/v1/players/{player_id}")
        assert response.status_code == 404


class TestLeagueAPI:
    """Интеграционные тесты League API"""

    @pytest.mark.asyncio
    async def test_create_and_get_league(self, api_client: httpx.AsyncClient) -> None:
        """Тест создания и получения лиги"""
        league_data = {
            "name": "Test League",
            "short_name": "TL",
            "country": "Test",
            "tier": 1,
            "confederation": "UEFA",
            "strength_coefficient": 1.0,
        }

        # Создание
        response = await api_client.post("/api/v1/leagues", json=league_data)
        assert response.status_code == 201

        data = response.json()
        league_id = data["id"]

        assert data["name"] == "Test League"
        assert data["tier"] == 1
        assert data["country"] == "Test"

        # Получение
        response = await api_client.get(f"/api/v1/leagues/{league_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == league_id
        assert data["is_top_league"] is True

    @pytest.mark.asyncio
    async def test_get_top_leagues(self, api_client: httpx.AsyncClient) -> None:
        """Тест получения топ лиг"""
        # Создаем топ лигу
        league_data = {
            "name": "Top League",
            "country": "England",
            "tier": 1,
            "confederation": "UEFA",
        }

        response = await api_client.post("/api/v1/leagues", json=league_data)
        assert response.status_code == 201

        # Создаем лигу не топ уровня
        league_data2 = {
            "name": "Second Division",
            "country": "England",
            "tier": 2,
            "confederation": "UEFA",
        }
        response = await api_client.post("/api/v1/leagues", json=league_data2)
        assert response.status_code == 201

        # Получаем топ лиги
        response = await api_client.get("/api/v1/leagues/top", params={"limit": 10})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # Все лиги должны быть tier=1
        assert all(league["tier"] == 1 for league in data)

    @pytest.mark.asyncio
    async def test_search_leagues(self, api_client: httpx.AsyncClient) -> None:
        """Тест поиска лиг"""
        # Создаем лигу
        league_data = {
            "name": "Premier League Test",
            "country": "England",
            "tier": 1,
            "confederation": "UEFA",
        }

        response = await api_client.post("/api/v1/leagues", json=league_data)
        assert response.status_code == 201

        # Поиск
        response = await api_client.get(
            "/api/v1/leagues/search", params={"name": "Premier"}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert any(league["name"] == "Premier League Test" for league in data)


class TestClubAPI:
    """Интеграционные тесты Club API"""

    @pytest.mark.asyncio
    async def test_create_and_get_club(self, api_client: httpx.AsyncClient) -> None:
        """Тест создания и получения клуба"""
        club_data = {
            "name": "Test FC",
            "short_name": "TFC",
            "founded_year": 1900,
            "country": "England",
            "city": "London",
            "stadium_name": "Test Stadium",
            "stadium_capacity": 50000,
        }

        # Создание
        response = await api_client.post("/api/v1/clubs", json=club_data)
        assert response.status_code == 201

        data = response.json()
        club_id = data["id"]

        assert data["name"] == "Test FC"
        assert data["city"] == "London"
        assert data["stadium_capacity"] == 50000

        # Получение
        response = await api_client.get(f"/api/v1/clubs/{club_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == club_id

    @pytest.mark.asyncio
    async def test_search_clubs(self, api_client: httpx.AsyncClient) -> None:
        """Тест поиска клубов"""
        # Создаем клуб
        club_data = {
            "name": "Manchester Test United",
            "country": "England",
            "city": "Manchester",
        }

        response = await api_client.post("/api/v1/clubs", json=club_data)
        assert response.status_code == 201

        # Поиск
        response = await api_client.get(
            "/api/v1/clubs/search", params={"name": "Manchester"}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert any(c["name"] == "Manchester Test United" for c in data)


class TestTeamAPI:
    """Интеграционные тесты Team API"""

    @pytest.mark.asyncio
    async def test_create_and_get_team(self, api_client: httpx.AsyncClient) -> None:
        """Тест создания и получения команды"""
        user_id = str(uuid4())
        team_data = {
            "name": "My Team",
            "description": "Test team",
        }

        # Создание
        response = await api_client.post(
            "/api/v1/teams",
            json=team_data,
            headers={"X-User-Id": user_id},
        )
        assert response.status_code == 201

        data = response.json()
        team_id = data["id"]

        assert data["name"] == "My Team"
        assert data["user_id"] == user_id
        assert data["player_count"] == 0

        # Получение
        response = await api_client.get(f"/api/v1/teams/{team_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == team_id

    @pytest.mark.asyncio
    async def test_get_user_teams(self, api_client: httpx.AsyncClient) -> None:
        """Тест получения команд пользователя"""
        user_id = str(uuid4())

        # Создаем команду
        team_data = {"name": "Team 1"}
        response = await api_client.post(
            "/api/v1/teams",
            json=team_data,
            headers={"X-User-Id": user_id},
        )
        assert response.status_code == 201

        # Получаем команды пользователя
        response = await api_client.get(
            "/api/v1/teams",
            headers={"X-User-Id": user_id},
        )
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_team_requires_user_id(self, api_client: httpx.AsyncClient) -> None:
        """Тест что команда требует X-User-Id"""
        team_data = {"name": "Team"}

        response = await api_client.post(
            "/api/v1/teams",
            json=team_data,
        )
        # Должна быть ошибка из-за отсутствия заголовка
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_add_player_to_team(self, api_client: httpx.AsyncClient) -> None:
        """Тест добавления игрока в команду"""
        user_id = str(uuid4())

        # Создаем команду
        team_data = {"name": "Team with Player"}
        response = await api_client.post(
            "/api/v1/teams",
            json=team_data,
            headers={"X-User-Id": user_id},
        )
        assert response.status_code == 201
        team_id = response.json()["id"]

        # Создаем игрока
        player_data = {
            "name": "Team Player",
            "date_of_birth": "1995-01-01",
            "nationality": "England",
            "position": "striker",
            "preferred_foot": "right",
            "height_cm": 180,
            "weight_kg": 75,
        }
        response = await api_client.post("/api/v1/players", json=player_data)
        assert response.status_code == 201
        player_id = response.json()["id"]

        # Добавляем игрока в команду
        response = await api_client.post(
            f"/api/v1/teams/{team_id}/players",
            json={"position": "striker", "player_id": player_id},
        )
        assert response.status_code == 200

        data = response.json()
        assert "striker" in data["squad"]
        assert player_id in data["squad"]["striker"]

    @pytest.mark.asyncio
    async def test_delete_team(self, api_client: httpx.AsyncClient) -> None:
        """Тест удаления команды"""
        user_id = str(uuid4())

        # Создаем команду
        team_data = {"name": "Delete Team"}
        response = await api_client.post(
            "/api/v1/teams",
            json=team_data,
            headers={"X-User-Id": user_id},
        )
        assert response.status_code == 201
        team_id = response.json()["id"]

        # Удаляем
        response = await api_client.delete(f"/api/v1/teams/{team_id}")
        assert response.status_code == 200

        # Проверяем что удалена
        response = await api_client.get(f"/api/v1/teams/{team_id}")
        assert response.status_code == 404
