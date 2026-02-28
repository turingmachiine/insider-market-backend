import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.player import Player
from src.domain.interfaces.repositories import IPlayerRepository
from src.domain.value_objects.position import Position
from src.infrastructure.db.tables import players_table

logger = logging.getLogger(__name__)


class PlayerRepository(IPlayerRepository):
    """Реализация репозитория игроков"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Player

    async def get_by_id(self, player_id: UUID) -> Optional[Player]:
        query = select(self.model).where(players_table.c.id == player_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_name(self, name: str) -> list[Player]:
        query = (
            select(self.model).where(players_table.c.name.ilike(f"%{name}%")).limit(100)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Player]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_position(
        self, position: Position, limit: int = 50
    ) -> list[Player]:
        query = (
            select(self.model)
            .where(players_table.c.position == position.value)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_league(self, league_id: UUID, limit: int = 100) -> list[Player]:
        query = (
            select(self.model)
            .where(players_table.c.current_league_id == league_id)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_club(self, club_id: UUID, limit: int = 50) -> list[Player]:
        query = (
            select(self.model)
            .where(players_table.c.current_club_id == club_id)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, player: Player) -> Player:
        self.session.add(player)
        await self.session.flush()
        return player

    async def delete_by_id(self, player_id: UUID) -> bool:
        player = await self.get_by_id(player_id)
        if not player:
            return False
        result = await self.delete(player)
        return result

    async def delete(self, player: Player) -> bool:
        await self.session.delete(player)
        await self.session.flush()
        return True
