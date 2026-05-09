import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.nsi_service.domain.entities.league import League
from src.nsi_service.domain.interfaces.repositories import ILeagueRepository
from src.nsi_service.infrastructure.db.tables import leagues_table

logger = logging.getLogger(__name__)


class LeagueRepository(ILeagueRepository):
    """Реализация репозитория лиг"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = League

    async def get_by_id(self, league_id: UUID) -> Optional[League]:
        query = select(self.model).where(leagues_table.c.id == league_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_name(self, name: str) -> Optional[League]:
        query = select(self.model).where(leagues_table.c.name.ilike(f"%{name}%"))
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(self, limit: int = 50, offset: int = 0) -> list[League]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_top_leagues(self, limit: int = 10) -> list[League]:
        query = select(self.model).where(leagues_table.c.tier == 1).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, league: League) -> League:
        self.session.add(league)
        await self.session.flush()
        return league
