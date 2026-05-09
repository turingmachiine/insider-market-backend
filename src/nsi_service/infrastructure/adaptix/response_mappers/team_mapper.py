from src.nsi_service.application.dto import TeamDTO
from src.nsi_service.presentation.api.v1.mappers import ITeamResponseMapper
from src.nsi_service.presentation.api.v1.schemas.team_schemas import TeamResponse


class TeamResponseMapper(ITeamResponseMapper):
    """Маппер TeamDTO в TeamResponse"""

    def to_response(self, dto: TeamDTO) -> TeamResponse:
        """Конвертировать TeamDTO в TeamResponse"""
        return TeamResponse(
            id=dto.id,
            name=dto.name,
            user_id=dto.user_id,
            description=dto.description,
            squad=dto.squad,
            player_count=dto.player_count,
        )
