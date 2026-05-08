from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.rating_service.domain.entities import RatingEvent
from src.backend.rating_service.domain.interfaces.repositories import (
    IRatingEventRepository,
)
from src.backend.rating_service.infrastructure.db.tables import rating_events_table


class RatingEventRepository(IRatingEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = RatingEvent

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> RatingEvent | None:
        query = select(self.model).where(
            rating_events_table.c.idempotency_key == idempotency_key
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_unprocessed(self, limit: int = 100) -> list[RatingEvent]:
        query = (
            select(self.model)
            .where(rating_events_table.c.processed_at.is_(None))
            .order_by(rating_events_table.c.occurred_at)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, event: RatingEvent) -> RatingEvent:
        self.session.add(event)
        await self.session.flush()
        return event
