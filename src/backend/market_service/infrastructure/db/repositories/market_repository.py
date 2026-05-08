from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.market_service.domain.entities import Market, MarketStatus
from src.backend.market_service.domain.interfaces.repositories import IMarketRepository
from src.backend.market_service.infrastructure.db.tables import markets_table


class MarketRepository(IMarketRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Market

    async def get_by_id(self, market_id: UUID) -> Market | None:
        query = select(self.model).where(markets_table.c.id == market_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_event_id(self, event_id: UUID) -> Market | None:
        query = select(self.model).where(markets_table.c.event_id == event_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: MarketStatus | None = None,
        event_id: UUID | None = None,
    ) -> list[Market]:
        query = select(self.model)
        if status is not None:
            query = query.where(markets_table.c.status == status)
        if event_id is not None:
            query = query.where(markets_table.c.event_id == event_id)
        query = (
            query.order_by(markets_table.c.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, market: Market) -> Market:
        self.session.add(market)
        await self.session.flush()
        return market
