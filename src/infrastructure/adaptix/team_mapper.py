"""Реализация маппера Team с использованием adaptix"""

from src.application.dto.team_dto import TeamDTO
from src.application.mappers import ITeamMapper
from src.domain.entities.team import Team


class TeamMapperImpl(ITeamMapper):
    """Реализация маппера Team с использованием adaptix"""

    def to_dto(self, entity: Team) -> TeamDTO:
        """Конвертировать Team в TeamDTO"""
        player_count = sum(len(players) for players in entity.squad.values())
        return TeamDTO(
            id=entity.id,
            name=entity.name,
            user_id=entity.user_id,
            description=entity.description,
            squad=entity.squad,
            player_count=player_count,
        )

    def to_entity(self, dto: TeamDTO) -> Team:
        """Конвертировать TeamDTO в Team"""
        return Team(
            id=dto.id,
            name=dto.name,
            user_id=dto.user_id,
            description=dto.description,
            squad=dto.squad,
        )
