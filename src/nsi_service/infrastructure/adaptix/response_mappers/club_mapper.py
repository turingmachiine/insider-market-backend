from src.nsi_service.application.dto import ClubDTO
from src.nsi_service.presentation.api.v1.mappers import IClubResponseMapper
from src.nsi_service.presentation.api.v1.schemas.club_schemas import ClubResponse


class ClubResponseMapper(IClubResponseMapper):
    """Маппер ClubDTO в ClubResponse"""

    def to_response(self, dto: ClubDTO) -> ClubResponse:
        """Конвертировать ClubDTO в ClubResponse"""
        return ClubResponse(
            id=dto.id,
            name=dto.name,
            short_name=dto.short_name,
            founded_year=dto.founded_year,
            country=dto.country,
            city=dto.city,
            stadium_name=dto.stadium_name,
            stadium_capacity=dto.stadium_capacity,
            league_id=dto.league_id,
            logo_url=dto.logo_url,
            website=dto.website,
            squad_market_value=dto.squad_market_value,
            average_age=dto.average_age,
            foreign_players_count=dto.foreign_players_count,
            national_team_players_count=dto.national_team_players_count,
        )
