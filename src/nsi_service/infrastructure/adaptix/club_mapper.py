"""Реализация маппера Club с использованием adaptix"""

from src.nsi_service.application.dto.club_dto import ClubDTO
from src.nsi_service.application.mappers import IClubMapper
from src.nsi_service.domain.entities.club import Club


class ClubMapperImpl(IClubMapper):
    """Реализация маппера Club с использованием adaptix"""

    def to_dto(self, entity: Club) -> ClubDTO:
        """Конвертировать Club в ClubDTO"""
        return ClubDTO(
            id=entity.id,
            name=entity.name,
            short_name=entity.short_name,
            founded_year=entity.founded_year,
            country=entity.country,
            city=entity.city,
            stadium_name=entity.stadium_name,
            stadium_capacity=entity.stadium_capacity,
            league_id=entity.league_id,
            logo_url=entity.logo_url,
            website=entity.website,
            squad_market_value=entity.squad_market_value,
            average_age=entity.average_age,
            foreign_players_count=entity.foreign_players_count,
            national_team_players_count=entity.national_team_players_count,
        )

    def to_entity(self, dto: ClubDTO) -> Club:
        """Конвертировать ClubDTO в Club"""
        return Club(
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
