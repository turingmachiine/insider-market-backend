"""Интеграционные тесты для репозиториев"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from src.nsi_service.domain.entities.club import Club
from src.nsi_service.domain.entities.league import League
from src.nsi_service.domain.entities.player import Player
from src.nsi_service.domain.entities.team import Team
from src.nsi_service.domain.services import PlayerService, TeamService
from src.nsi_service.domain.value_objects.position import Position


@pytest.mark.asyncio
class TestLeagueRepository:
    """Интеграционные тесты для LeagueRepository"""

    async def test_save_and_get_league(
        self,
        league_repository,
        sample_league_entity: League,
    ) -> None:
        """Тест сохранения и получения лиги"""
        # Сохранение
        saved = await league_repository.save(sample_league_entity)

        assert saved.id == sample_league_entity.id
        assert saved.name == sample_league_entity.name
        assert saved.country == sample_league_entity.country

        # Получение по ID
        retrieved = await league_repository.get_by_id(sample_league_entity.id)

        assert retrieved is not None
        assert retrieved.id == sample_league_entity.id
        assert retrieved.name == sample_league_entity.name

    async def test_get_top_leagues(
        self,
        league_repository,
        sample_league_entity: League,
    ) -> None:
        """Тест получения топ лиг"""
        # Создаем несколько лиг
        league2 = League(
            id=uuid4(),
            name="La Liga",
            short_name="La Liga",
            country="Spain",
            tier=1,
            confederation="UEFA",
            logo_url=None,
        )
        league3 = League(
            id=uuid4(),
            name="Second Division",
            short_name="SD",
            country="England",
            tier=2,
            confederation="UEFA",
            logo_url=None,
        )

        await league_repository.save(sample_league_entity)
        await league_repository.save(league2)
        await league_repository.save(league3)

        # Получаем топ лиги
        top_leagues = await league_repository.get_top_leagues(limit=10)

        assert len(top_leagues) == 2  # Только tier=1
        assert all(league.tier == 1 for league in top_leagues)

    async def test_get_all_leagues(
        self,
        league_repository,
        sample_league_entity: League,
    ) -> None:
        """Тест получения всех лиг с пагинацией"""
        # Создаем несколько лиг
        for i in range(5):
            league = League(
                id=uuid4(),
                name=f"League {i}",
                short_name=f"L{i}",
                country="Test",
                tier=1,
                confederation="UEFA",
                logo_url=None,
            )
            await league_repository.save(league)

        await league_repository.save(sample_league_entity)

        # Получаем с пагинацией
        all_leagues = await league_repository.get_all(limit=10, offset=0)

        assert len(all_leagues) == 6  # 5 + sample_league


@pytest.mark.asyncio
class TestClubRepository:
    """Интеграционные тесты для ClubRepository"""

    async def test_save_and_get_club(
        self,
        club_repository,
        sample_club_entity: Club,
    ) -> None:
        """Тест сохранения и получения клуба"""
        saved = await club_repository.save(sample_club_entity)

        assert saved.id == sample_club_entity.id
        assert saved.name == sample_club_entity.name

        retrieved = await club_repository.get_by_id(sample_club_entity.id)

        assert retrieved is not None
        assert retrieved.name == sample_club_entity.name

    async def test_get_by_name(
        self,
        club_repository,
        sample_club_entity: Club,
    ) -> None:
        """Тест поиска клуба по имени"""
        await club_repository.save(sample_club_entity)

        # Поиск по полному имени
        found = await club_repository.get_by_name("Manchester City")

        assert found is not None
        assert found.id == sample_club_entity.id

        # Поиск по части имени
        found_partial = await club_repository.get_by_name("Man")

        assert found_partial is not None
        assert found_partial.id == sample_club_entity.id

    async def test_get_clubs_by_league(
        self,
        club_repository,
        league_repository,
        sample_league_entity: League,
        sample_club_entity: Club,
    ) -> None:
        """Тест получения клубов лиги"""
        # Сначала сохраняем лигу
        await league_repository.save(sample_league_entity)

        # Создаем клуб с этой лигой
        club_with_league = Club(
            id=uuid4(),
            name="Club with League",
            short_name="CWL",
            founded_year=1900,
            country="Test",
            city="Test",
            stadium_name=None,
            stadium_capacity=None,
            league_id=sample_league_entity.id,
            logo_url=None,
            website=None,
            squad_market_value=None,
            average_age=None,
            foreign_players_count=None,
            national_team_players_count=None,
        )
        await club_repository.save(club_with_league)

        # Создаем клуб без лиги
        await club_repository.save(sample_club_entity)

        # Получаем клубы конкретной лиги
        clubs = await club_repository.get_by_league(
            sample_league_entity.id,
            limit=10,
        )

        assert len(clubs) == 1
        assert clubs[0].id == club_with_league.id


@pytest.mark.asyncio
class TestPlayerRepository:
    """Интеграционные тесты для PlayerRepository"""

    async def test_save_and_get_player(
        self,
        player_repository,
        sample_player_entity: Player,
    ) -> None:
        """Тест сохранения и получения игрока"""
        saved = await player_repository.save(sample_player_entity)

        assert saved.id == sample_player_entity.id
        assert saved.name == sample_player_entity.name
        assert saved.position == sample_player_entity.position

        retrieved = await player_repository.get_by_id(sample_player_entity.id)

        assert retrieved is not None
        assert retrieved.name == sample_player_entity.name

    async def test_get_by_name(
        self,
        player_repository,
        sample_player_entity: Player,
    ) -> None:
        """Тест поиска игрока по имени"""
        await player_repository.save(sample_player_entity)

        # Поиск по полному имени
        found = await player_repository.get_by_name("Haaland")

        assert len(found) == 1
        assert found[0].id == sample_player_entity.id

        # Поиск по части имени
        found_partial = await player_repository.get_by_name("Erling")

        assert len(found_partial) == 1

    async def test_get_by_position(
        self,
        player_repository,
        sample_player_entity: Player,
    ) -> None:
        """Тест получения игроков по позиции"""
        await player_repository.save(sample_player_entity)

        # Создаем игрока на другой позиции
        player2 = Player(
            id=uuid4(),
            name="Kevin De Bruyne",
            first_name="Kevin",
            last_name="De Bruyne",
            date_of_birth=date(1991, 6, 28),
            nationality="Belgium",
            position=Position.CM,
            preferred_foot="right",
            height_cm=181,
            weight_kg=70,
            current_club_id=None,
            current_league_id=None,
            market_value=Decimal("50000000"),
            contract_until=date(2025, 6, 30),
            shirt_number=17,
            appearances=0,
            goals=0,
            assists=0,
            minutes_played=0,
            xg=0.0,
            xa=0.0,
            xg_per_90=0.0,
            xa_per_90=0.0,
            league_strength_coefficient=1.0,
        )
        await player_repository.save(player2)

        # Получаем игроков на позиции ST
        strikers = await player_repository.get_by_position(Position.ST, limit=10)

        assert len(strikers) == 1
        assert strikers[0].id == sample_player_entity.id

    async def test_get_by_league(
        self,
        player_repository,
        league_repository,
        sample_league_entity: League,
        sample_player_entity: Player,
    ) -> None:
        """Тест получения игроков лиги"""
        # Сначала сохраняем лигу
        await league_repository.save(sample_league_entity)

        # Создаем игрока с этой лигой
        player_with_league = Player(
            id=uuid4(),
            name="Player with League",
            first_name="Player",
            last_name="League",
            date_of_birth=date(1995, 1, 1),
            nationality="Test",
            position=Position.ST,
            preferred_foot="right",
            height_cm=180,
            weight_kg=75,
            current_club_id=None,
            current_league_id=sample_league_entity.id,
            market_value=Decimal("50000000"),
            contract_until=date(2025, 6, 30),
            shirt_number=10,
            appearances=0,
            goals=0,
            assists=0,
            minutes_played=0,
            xg=0.0,
            xa=0.0,
            xg_per_90=0.0,
            xa_per_90=0.0,
            league_strength_coefficient=1.0,
        )
        await player_repository.save(player_with_league)

        players = await player_repository.get_by_league(
            sample_league_entity.id,
            limit=10,
        )

        assert len(players) == 1
        assert players[0].id == player_with_league.id

    async def test_update_player(
        self,
        player_repository,
        player_service: PlayerService,
        sample_player_entity: Player,
    ) -> None:
        """Тест обновления игрока"""
        # Сохраняем
        await player_repository.save(sample_player_entity)

        # Обновляем
        updated_player = player_service.update_stats(
            player=sample_player_entity,
            appearances=5,
            goals=3,
            assists=2,
            minutes_played=450,
        )

        saved = await player_repository.save(updated_player)

        assert saved.appearances == 35
        assert saved.goals == 28

    async def test_delete_player(
        self,
        player_repository,
    ) -> None:
        """Тест удаления игрока"""
        # Создаем игрока без FK
        player = Player(
            id=uuid4(),
            name="Delete Me",
            first_name="Delete",
            last_name="Me",
            date_of_birth=date(1995, 1, 1),
            nationality="Test",
            position=Position.ST,
            preferred_foot="right",
            height_cm=180,
            weight_kg=75,
            current_club_id=None,
            current_league_id=None,
            market_value=Decimal("50000000"),
            contract_until=date(2025, 6, 30),
            shirt_number=10,
            appearances=0,
            goals=0,
            assists=0,
            minutes_played=0,
            xg=0.0,
            xa=0.0,
            xg_per_90=0.0,
            xa_per_90=0.0,
            league_strength_coefficient=1.0,
        )

        # Сохраняем
        saved = await player_repository.save(player)

        # Проверяем что существует
        retrieved = await player_repository.get_by_id(saved.id)
        assert retrieved is not None

        # Удаляем
        deleted = await player_repository.delete_by_id(saved.id)
        assert deleted is True

        # Проверяем что удален
        retrieved = await player_repository.get_by_id(saved.id)
        assert retrieved is None


@pytest.mark.asyncio
class TestTeamRepository:
    """Интеграционные тесты для TeamRepository"""

    async def test_save_and_get_team(
        self,
        team_repository,
        sample_team_entity: Team,
    ) -> None:
        """Тест сохранения и получения команды"""
        saved = await team_repository.save(sample_team_entity)

        assert saved.id == sample_team_entity.id
        assert saved.name == sample_team_entity.name
        assert saved.user_id == sample_team_entity.user_id

        retrieved = await team_repository.get_by_id(sample_team_entity.id)

        assert retrieved is not None
        assert retrieved.name == sample_team_entity.name

    async def test_get_by_user(
        self,
        team_repository,
        sample_team_entity: Team,
    ) -> None:
        """Тест получения команд пользователя"""
        await team_repository.save(sample_team_entity)

        # Создаем еще одну команду того же пользователя
        team2 = Team(
            id=uuid4(),
            name="Second Team",
            user_id=sample_team_entity.user_id,
            description="Another team",
            squad={},
            created_at=date.today(),
            updated_at=date.today(),
        )
        await team_repository.save(team2)

        # Создаем команду другого пользователя
        team3 = Team(
            id=uuid4(),
            name="Other Team",
            user_id=uuid4(),
            description="Other",
            squad={},
            created_at=date.today(),
            updated_at=date.today(),
        )
        await team_repository.save(team3)

        # Получаем команды конкретного пользователя
        user_teams = await team_repository.get_by_user(sample_team_entity.user_id)

        assert len(user_teams) == 2

    async def test_update_team(
        self,
        team_repository,
        team_service: TeamService,
        sample_team_entity: Team,
    ) -> None:
        """Тест обновления команды"""
        # Сохраняем
        await team_repository.save(sample_team_entity)

        # Обновляем
        new_player_id = uuid4()
        updated_team = team_service.add_player(
            sample_team_entity, Position.ST.value, new_player_id
        )

        saved = await team_repository.save(updated_team)

        assert str(new_player_id) in saved.squad.get(Position.ST.value, [])

    async def test_delete_team(
        self,
        team_repository,
        sample_team_entity: Team,
    ) -> None:
        """Тест удаления команды"""
        # Сохраняем
        await team_repository.save(sample_team_entity)

        # Удаляем
        deleted = await team_repository.delete_by_id(sample_team_entity.id)
        assert deleted is True

        # Проверяем что удалена
        retrieved = await team_repository.get_by_id(sample_team_entity.id)
        assert retrieved is None
