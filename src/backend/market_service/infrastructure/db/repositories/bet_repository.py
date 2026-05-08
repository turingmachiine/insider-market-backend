from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.market_service.domain.entities import Bet
from src.backend.market_service.domain.interfaces.repositories import IBetRepository
from src.backend.market_service.infrastructure.db.tables import bets_table


class BetRepository(IBetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Bet

    async def get_by_market(
        self,
        market_id: UUID,
        limit: int = 100,
        offset: int = 0,
        user_id: UUID | None = None,
    ) -> list[Bet]:
        query = select(self.model).where(bets_table.c.market_id == market_id)
        if user_id is not None:
            query = query.where(bets_table.c.user_id == user_id)
        query = (
            query.order_by(bets_table.c.created_at.desc()).offset(offset).limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, bet: Bet) -> Bet:
        self.session.add(bet)
        await self.session.flush()
        return bet
