import logging
from typing import Optional
from uuid import UUID

from src.application.dto import CreateLeagueDTO, LeagueDTO
from src.application.mappers import ILeagueMapper
from src.domain.interfaces.repositories import ILeagueRepository

logger = logging.getLogger(__name__)


class LeagueUseCases:
    """Use cases для лиг"""

    def __init__(
        self, league_repository: ILeagueRepository, league_mapper: ILeagueMapper
    ):
        self.league_repo = league_repository
        self.league_mapper = league_mapper

    async def get_league(self, league_id: UUID) -> Optional[LeagueDTO]:
        """Получить лигу по ID"""
        league = await self.league_repo.get_by_id(league_id)
        return self.league_mapper.to_dto(league) if league else None

    async def search_leagues(self, name: str) -> list[LeagueDTO]:
        """Поиск лиг по имени"""
        league = await self.league_repo.get_by_name(name)
        return [self.league_mapper.to_dto(league)] if league else []

    async def get_all_leagues(
        self, limit: int = 50, offset: int = 0
    ) -> list[LeagueDTO]:
        """Получить все лиги с пагинацией"""
        leagues = await self.league_repo.get_all(limit=limit, offset=offset)
        return [self.league_mapper.to_dto(league) for league in leagues]

    async def get_top_leagues(self, limit: int = 10) -> list[LeagueDTO]:
        """Получить топ лиги"""
        leagues = await self.league_repo.get_top_leagues(limit=limit)
        return [self.league_mapper.to_dto(league) for league in leagues]

    async def create_league(self, dto: CreateLeagueDTO) -> LeagueDTO:
        """Создать новую лигу"""
        from uuid import uuid4

        from src.domain.entities.league import League

        league = League(
            id=uuid4(),
            name=dto.name,
            short_name=dto.short_name,
            country=dto.country,
            tier=dto.tier,
            confederation=dto.confederation,
            logo_url=dto.logo_url,
            strength_coefficient=dto.strength_coefficient,
            current_season=dto.current_season,
            season_start=dto.season_start,
            season_end=dto.season_end,
        )

        saved_league = await self.league_repo.save(league)
        return self.league_mapper.to_dto(saved_league)
