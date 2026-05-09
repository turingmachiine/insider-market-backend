"""Тесты для доменных сущностей"""

from datetime import date
from uuid import uuid4

from src.nsi_service.domain.entities.club import Club
from src.nsi_service.domain.entities.league import League
from src.nsi_service.domain.entities.player import Player
from src.nsi_service.domain.entities.team import Team
from src.nsi_service.domain.value_objects.position import Position


class TestPlayer:
    """Тесты для сущности Player"""

    def test_player_creation(self, sample_player: Player) -> None:
        """Тест создания игрока"""
        assert sample_player.name == "Erling Haaland"
        assert sample_player.position == Position.ST
        assert sample_player.age == 25  # На 2026 год

    def test_player_full_name(self, sample_player: Player) -> None:
        """Тест полного имени"""
        assert sample_player.full_name == "Erling Haaland"

    def test_player_age_calculation(self) -> None:
        """Тест расчета возраста"""
        player = Player(
            id=uuid4(),
            name="Test Player",
            first_name="Test",
            last_name="Player",
            date_of_birth=date(2000, 1, 1),
            nationality="Test",
            position=Position.ST,
            preferred_foot="right",
            height_cm=180,
            weight_kg=75,
            current_club_id=None,
            current_league_id=None,
            market_value=None,
            contract_until=None,
            shirt_number=None,
        )
        # Возраст зависит от текущей даты
        assert player.age >= 25

    def test_player_position_enum(self) -> None:
        """Тест enum позиций"""
        assert Position.ST.value == "striker"
        assert Position.CM.value == "central_midfielder"
        assert Position.GK.value == "goalkeeper"

    def test_position_category(self) -> None:
        """Тест категорий позиций"""
        assert Position.get_main_category(Position.GK) == "GK"
        assert Position.get_main_category(Position.CB) == "DEF"
        assert Position.get_main_category(Position.CM) == "MID"
        assert Position.get_main_category(Position.ST) == "FWD"


class TestClub:
    """Тесты для сущности Club"""

    def test_club_creation(self, sample_club: Club) -> None:
        """Тест создания клуба"""
        assert sample_club.name == "Manchester City"
        assert sample_club.display_name == "Man City"

    def test_club_display_name_without_short(self) -> None:
        """Тест отображаемого имени без короткого"""
        club = Club(
            id=uuid4(),
            name="Full Club Name",
            short_name=None,
            founded_year=1900,
            country="Test",
            city="Test City",
            stadium_name=None,
            stadium_capacity=None,
            league_id=None,
            logo_url=None,
            website=None,
            squad_market_value=None,
            average_age=None,
            foreign_players_count=None,
            national_team_players_count=None,
        )
        assert club.display_name == "Full Club Name"


class TestLeague:
    """Тесты для сущности League"""

    def test_league_creation(self, sample_league: League) -> None:
        """Тест создания лиги"""
        assert sample_league.name == "Premier League"
        assert sample_league.display_name == "EPL"
        assert sample_league.is_top_league is True

    def test_league_not_top_tier(self) -> None:
        """Тест лиги не топ уровня"""
        league = League(
            id=uuid4(),
            name="Second Division",
            short_name="SD",
            country="Test",
            tier=2,
            confederation="UEFA",
            logo_url=None,
        )
        assert league.is_top_league is False


class TestTeam:
    """Тесты для сущности Team"""

    def test_team_creation(self) -> None:
        """Тест создания команды"""
        team = Team(
            id=uuid4(),
            name="Test Team",
            user_id=uuid4(),
            description="Test",
            squad={Position.ST.value: [str(uuid4())]},
        )
        assert team.name == "Test Team"
        assert len(team.squad) > 0
