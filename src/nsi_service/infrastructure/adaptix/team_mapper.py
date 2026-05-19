"""Реализация маппера Team с использованием adaptix"""

from src.nsi_service.application.dto.team_dto import TeamDTO
from src.nsi_service.application.mappers import ITeamMapper
from src.nsi_service.domain.entities.team import Team


class TeamMapperImpl(ITeamMapper):
    """Реализация маппера Team с использованием adaptix"""

    def to_dto(self, entity: Team) -> TeamDTO:
        """Конвертировать Team в TeamDTO"""
        squad = self._normalize_squad(entity.squad)
        player_count = sum(len(players) for players in squad.values())
        return TeamDTO(
            id=entity.id,
            name=entity.name,
            user_id=entity.user_id,
            description=entity.description,
            squad=squad,
            player_count=player_count,
        )

    @staticmethod
    def _normalize_squad(squad: dict | None) -> dict:
        if not isinstance(squad, dict):
            return {}
        normalized: dict[str, list[str]] = {}
        for position, players in squad.items():
            if players is None:
                normalized[str(position)] = []
            elif isinstance(players, list):
                normalized[str(position)] = [str(player_id) for player_id in players]
            else:
                normalized[str(position)] = [str(players)]
        return normalized

    def to_entity(self, dto: TeamDTO) -> Team:
        """Конвертировать TeamDTO в Team"""
        return Team(
            id=dto.id,
            name=dto.name,
            user_id=dto.user_id,
            description=dto.description,
            squad=dto.squad,
        )
