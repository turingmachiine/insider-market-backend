import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.nsi_service.domain.entities.club import Club
from src.nsi_service.domain.interfaces.repositories import IClubRepository
from src.nsi_service.infrastructure.db.tables import clubs_table

logger = logging.getLogger(__name__)


class ClubRepository(IClubRepository):
    """Реализация репозитория клубов"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Club

    async def get_by_id(self, club_id: UUID) -> Optional[Club]:
        query = select(self.model).where(clubs_table.c.id == club_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_name(self, name: str) -> Optional[Club]:
        query = select(self.model).where(clubs_table.c.name.ilike(f"%{name}%"))
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Club]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_league(self, league_id: UUID, limit: int = 50) -> list[Club]:
        query = (
            select(self.model).where(clubs_table.c.league_id == league_id).limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, club: Club) -> Club:
        self.session.add(club)
        await self.session.flush()
        return club
