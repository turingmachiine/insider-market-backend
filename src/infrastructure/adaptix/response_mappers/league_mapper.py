from src.application.dto import LeagueDTO
from src.presentation.api.v1.mappers import ILeagueResponseMapper
from src.presentation.api.v1.schemas.league_schemas import LeagueResponse


class LeagueResponseMapper(ILeagueResponseMapper):
    """Маппер LeagueDTO в LeagueResponse"""

    def to_response(self, dto: LeagueDTO) -> LeagueResponse:
        """Конвертировать LeagueDTO в LeagueResponse"""
        return LeagueResponse(
            id=dto.id,
            name=dto.name,
            short_name=dto.short_name,
            country=dto.country,
            tier=dto.tier,
            confederation=dto.confederation,
            logo_url=dto.logo_url,
            strength_coefficient=dto.strength_coefficient,
            current_season=dto.current_season,
            is_top_league=dto.is_top_league,
        )
