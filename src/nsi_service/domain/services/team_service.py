from uuid import UUID

from src.nsi_service.domain.entities import Team


class TeamService:
    @staticmethod
    def get_players_by_position(team: Team, position: str) -> list[str]:
        """Получить игроков по позиции (возвращает строки)"""
        return team.squad.get(position, [])

    @staticmethod
    def add_player(team: Team, position: str, player_id: UUID) -> "Team":
        """Добавить игрока на позицию"""
        player_id_str = str(player_id)
        if position not in team.squad:
            team.squad[position] = []
        if player_id_str not in team.squad[position]:
            team.squad[position].append(player_id_str)
        return team

    @staticmethod
    def remove_player(team: Team, position: str, player_id: UUID) -> "Team":
        """Удалить игрока из команды"""
        player_id_str = str(player_id)
        if position in team.squad and player_id_str in team.squad[position]:
            team.squad[position].remove(player_id_str)
            if not team.squad[position]:
                del team.squad[position]
        return team
