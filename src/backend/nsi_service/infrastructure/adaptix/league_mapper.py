"""Реализация маппера League с использованием adaptix"""

from src.backend.nsi_service.application.dto.league_dto import LeagueDTO
from src.backend.nsi_service.application.mappers import ILeagueMapper
from src.backend.nsi_service.domain.entities.league import League


class LeagueMapperImpl(ILeagueMapper):
    """Реализация маппера League с использованием adaptix"""

    def to_dto(self, entity: League) -> LeagueDTO:
        """Конвертировать League в LeagueDTO"""
        return LeagueDTO(
            id=entity.id,
            name=entity.name,
            short_name=entity.short_name,
            country=entity.country,
            tier=entity.tier,
            confederation=entity.confederation,
            logo_url=entity.logo_url,
            strength_coefficient=entity.strength_coefficient,
            current_season=entity.current_season,
            is_top_league=entity.is_top_league,
        )

    def to_entity(self, dto: LeagueDTO) -> League:
        """Конвертировать LeagueDTO в League"""
        return League(
            id=dto.id,
            name=dto.name,
            short_name=dto.short_name,
            country=dto.country,
            tier=dto.tier,
            confederation=dto.confederation,
            logo_url=dto.logo_url,
            strength_coefficient=dto.strength_coefficient,
            current_season=dto.current_season,
        )
