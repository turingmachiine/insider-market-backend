"""Репозиторий команд"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.nsi_service.domain.entities.team import Team
from src.backend.nsi_service.domain.interfaces.repositories import ITeamRepository
from src.backend.nsi_service.infrastructure.db.tables import teams_table

logger = logging.getLogger(__name__)


class TeamRepository(ITeamRepository):
    """Реализация репозитория команд"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Team

    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        query = select(self.model).where(teams_table.c.id == team_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_user(self, user_id: UUID) -> list[Team]:
        query = select(self.model).where(teams_table.c.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, team: Team) -> Team:
        self.session.add(team)
        await self.session.flush()
        return team

    async def delete_by_id(self, team_id: UUID) -> bool:
        team = await self.get_by_id(team_id)
        if not team:
            return False
        result = await self.delete(team)
        return result

    async def delete(self, team: Team) -> bool:
        await self.session.delete(team)
        await self.session.flush()
        return True
