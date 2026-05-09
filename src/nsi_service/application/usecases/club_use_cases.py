import logging
from typing import Optional
from uuid import UUID

from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager
from src.nsi_service.application.dto import ClubDTO, CreateClubDTO
from src.nsi_service.application.mappers import IClubMapper
from src.nsi_service.domain.interfaces.repositories import (
    IClubRepository,
    IPlayerRepository,
)

logger = logging.getLogger(__name__)


@use_case
class ClubUseCases(HasTransactionManager):
    """Use cases для клубов"""

    club_repository: IClubRepository
    player_repository: IPlayerRepository
    club_mapper: IClubMapper
    transaction_manager: TransactionManager

    async def get_club(self, club_id: UUID) -> Optional[ClubDTO]:
        """Получить клуб по ID"""
        club = await self.club_repository.get_by_id(club_id)
        return self.club_mapper.to_dto(club) if club else None

    async def search_clubs(self, name: str) -> list[ClubDTO]:
        """Поиск клубов по имени"""
        club = await self.club_repository.get_by_name(name)
        return [self.club_mapper.to_dto(club)] if club else []

    async def get_all_clubs(self, limit: int = 100, offset: int = 0) -> list[ClubDTO]:
        """Получить все клубы с пагинацией"""
        clubs = await self.club_repository.get_all(limit=limit, offset=offset)
        return [self.club_mapper.to_dto(c) for c in clubs]

    async def get_clubs_by_league(
        self, league_id: UUID, limit: int = 50
    ) -> list[ClubDTO]:
        """Получить клубы лиги"""
        clubs = await self.club_repository.get_by_league(league_id, limit=limit)
        return [self.club_mapper.to_dto(c) for c in clubs]

    @transactional()
    async def create_club(self, dto: CreateClubDTO) -> ClubDTO:
        """Создать новый клуб"""
        from uuid import uuid4

        from src.nsi_service.domain.entities.club import Club

        club = Club(
            id=uuid4(),
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

        saved_club = await self.club_repository.save(club)
        return self.club_mapper.to_dto(saved_club)
