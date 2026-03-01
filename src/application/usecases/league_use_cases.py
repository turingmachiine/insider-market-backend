import logging
from typing import Optional
from uuid import UUID

from src.application.decorators import transactional, use_case
from src.application.dto import CreateLeagueDTO, LeagueDTO
from src.application.mappers import ILeagueMapper
from src.application.protocols import HasTransactionManager
from src.domain.interfaces.repositories import ILeagueRepository
from src.domain.interfaces.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@use_case
class LeagueUseCases(HasTransactionManager):
    """Use cases для лиг"""

    league_repository: ILeagueRepository
    league_mapper: ILeagueMapper
    transaction_manager: TransactionManager

    async def get_league(self, league_id: UUID) -> Optional[LeagueDTO]:
        """Получить лигу по ID"""
        league = await self.league_repository.get_by_id(league_id)
        return self.league_mapper.to_dto(league) if league else None

    async def search_leagues(self, name: str) -> list[LeagueDTO]:
        """Поиск лиг по имени"""
        league = await self.league_repository.get_by_name(name)
        return [self.league_mapper.to_dto(league)] if league else []

    async def get_all_leagues(
        self, limit: int = 50, offset: int = 0
    ) -> list[LeagueDTO]:
        """Получить все лиги с пагинацией"""
        leagues = await self.league_repository.get_all(limit=limit, offset=offset)
        return [self.league_mapper.to_dto(league) for league in leagues]

    async def get_top_leagues(self, limit: int = 10) -> list[LeagueDTO]:
        """Получить топ лиги"""
        leagues = await self.league_repository.get_top_leagues(limit=limit)
        return [self.league_mapper.to_dto(league) for league in leagues]

    @transactional()
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

        saved_league = await self.league_repository.save(league)
        return self.league_mapper.to_dto(saved_league)
