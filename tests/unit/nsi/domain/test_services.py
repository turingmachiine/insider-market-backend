from uuid import uuid4

from src.backend.nsi_service.domain.entities import Player, Team
from src.backend.nsi_service.domain.services import PlayerService, TeamService
from src.backend.nsi_service.domain.value_objects import Position


class TestPlayerService:
    """Тесты для сервиса PlayerService"""

    def test_player_update_stats(
        self, sample_player: Player, player_service: PlayerService
    ) -> None:
        """Тест обновления статистики"""
        sample_player_appearances = sample_player.appearances
        sample_player_goals = sample_player.goals
        sample_player_assists = sample_player.assists
        sample_player_minutes_played = sample_player.minutes_played

        player_service.update_stats(
            player=sample_player,
            appearances=5,
            goals=3,
            assists=2,
            minutes_played=450,
        )

        assert sample_player.appearances == sample_player_appearances + 5
        assert sample_player.goals == sample_player_goals + 3
        assert sample_player.assists == sample_player_assists + 2
        assert sample_player.minutes_played == sample_player_minutes_played + 450


class TestTeamService:
    """Тесты для сервиса TeamService"""

    def test_team_add_player(self, team_service: TeamService) -> None:
        """Тест добавления игрока"""
        # Создаем новую команду для теста
        original_player_id = uuid4()
        team = Team(
            id=uuid4(),
            name="Test Team",
            user_id=uuid4(),
            description="Test",
            squad={Position.ST.value: [str(original_player_id)]},
        )

        new_player_id = uuid4()
        updated_team = team_service.add_player(team, Position.ST.value, new_player_id)

        # Новый игрок должен быть в обновленной команде
        assert str(new_player_id) in updated_team.squad.get(Position.ST.value, [])

        # Оригинальный игрок тоже должен остаться
        assert str(original_player_id) in updated_team.squad.get(Position.ST.value, [])

    def test_team_remove_player(self, team_service: TeamService) -> None:
        """Тест удаления игрока"""
        player1_id = uuid4()
        player2_id = uuid4()
        team = Team(
            id=uuid4(),
            name="Test Team",
            user_id=uuid4(),
            description="Test",
            squad={Position.CB.value: [str(player1_id), str(player2_id)]},
        )

        updated_team = team_service.remove_player(team, Position.CB.value, player1_id)

        assert str(player1_id) not in updated_team.squad.get(Position.CB.value, [])
        assert str(player2_id) in updated_team.squad.get(Position.CB.value, [])

    def test_team_get_players_by_position(self, team_service: TeamService) -> None:
        """Тест получения игроков по позиции"""
        player_id = uuid4()
        team = Team(
            id=uuid4(),
            name="Test Team",
            user_id=uuid4(),
            description="Test",
            squad={Position.ST.value: [str(player_id)]},
        )
        players = team_service.get_players_by_position(team, Position.ST.value)
        assert isinstance(players, list)
        assert str(player_id) in players
