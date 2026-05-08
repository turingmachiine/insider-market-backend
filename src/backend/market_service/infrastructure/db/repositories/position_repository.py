from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.market_service.domain.entities import MarketSide, Position
from src.backend.market_service.domain.interfaces.repositories import (
    IPositionRepository,
)
from src.backend.market_service.infrastructure.db.tables import positions_table


class PositionRepository(IPositionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Position

    async def get_by_market_user_side(
        self,
        market_id: UUID,
        user_id: UUID,
        side: MarketSide,
    ) -> Position | None:
        query = select(self.model).where(
            positions_table.c.market_id == market_id,
            positions_table.c.user_id == user_id,
            positions_table.c.side == side,
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_market(self, market_id: UUID) -> list[Position]:
        query = select(self.model).where(positions_table.c.market_id == market_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user(self, user_id: UUID) -> list[Position]:
        query = select(self.model).where(positions_table.c.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, position: Position) -> Position:
        self.session.add(position)
        await self.session.flush()
        return position
