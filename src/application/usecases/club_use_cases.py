import logging
from typing import Optional
from uuid import UUID

from src.application.dto import ClubDTO, CreateClubDTO
from src.application.mappers import IClubMapper
from src.domain.interfaces.repositories import IClubRepository, IPlayerRepository

logger = logging.getLogger(__name__)


class ClubUseCases:
    """Use cases для клубов"""

    def __init__(
        self,
        club_repository: IClubRepository,
        player_repository: IPlayerRepository,
        club_mapper: IClubMapper,
    ):
        self.club_repo = club_repository
        self.player_repo = player_repository
        self.club_mapper = club_mapper

    async def get_club(self, club_id: UUID) -> Optional[ClubDTO]:
        """Получить клуб по ID"""
        club = await self.club_repo.get_by_id(club_id)
        return self.club_mapper.to_dto(club) if club else None

    async def search_clubs(self, name: str) -> list[ClubDTO]:
        """Поиск клубов по имени"""
        club = await self.club_repo.get_by_name(name)
        return [self.club_mapper.to_dto(club)] if club else []

    async def get_all_clubs(self, limit: int = 100, offset: int = 0) -> list[ClubDTO]:
        """Получить все клубы с пагинацией"""
        clubs = await self.club_repo.get_all(limit=limit, offset=offset)
        return [self.club_mapper.to_dto(c) for c in clubs]

    async def get_clubs_by_league(
        self, league_id: UUID, limit: int = 50
    ) -> list[ClubDTO]:
        """Получить клубы лиги"""
        clubs = await self.club_repo.get_by_league(league_id, limit=limit)
        return [self.club_mapper.to_dto(c) for c in clubs]

    async def create_club(self, dto: CreateClubDTO) -> ClubDTO:
        """Создать новый клуб"""
        from uuid import uuid4

        from src.domain.entities.club import Club

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

        saved_club = await self.club_repo.save(club)
        return self.club_mapper.to_dto(saved_club)
