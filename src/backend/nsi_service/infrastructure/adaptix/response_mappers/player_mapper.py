from src.backend.nsi_service.application.dto import PlayerDTO
from src.backend.nsi_service.presentation.api.v1.mappers import IPlayerResponseMapper
from src.backend.nsi_service.presentation.api.v1.schemas.player_schemas import (
    PlayerResponse,
)


class PlayerResponseMapper(IPlayerResponseMapper):
    """Маппер PlayerDTO в PlayerResponse"""

    def to_response(self, dto: PlayerDTO) -> PlayerResponse:
        """Конвертировать PlayerDTO в PlayerResponse"""
        return PlayerResponse(
            id=dto.id,
            name=dto.name,
            first_name=dto.first_name,
            last_name=dto.last_name,
            date_of_birth=dto.date_of_birth,
            nationality=dto.nationality,
            position=dto.position,
            preferred_foot=dto.preferred_foot,
            height_cm=dto.height_cm,
            weight_kg=dto.weight_kg,
            current_club_id=dto.current_club_id,
            current_league_id=dto.current_league_id,
            market_value=dto.market_value,
            contract_until=dto.contract_until,
            shirt_number=dto.shirt_number,
            appearances=dto.appearances,
            goals=dto.goals,
            assists=dto.assists,
            minutes_played=dto.minutes_played,
            xg=dto.xg,
            xa=dto.xa,
            xg_per_90=dto.xg_per_90,
            xa_per_90=dto.xa_per_90,
            league_strength_coefficient=dto.league_strength_coefficient,
            age=dto.age,
        )
