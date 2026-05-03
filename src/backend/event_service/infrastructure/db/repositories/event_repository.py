from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.event_service.domain.entities import Event, EventStatus
from src.backend.event_service.domain.interfaces.repositories import IEventRepository
from src.backend.event_service.infrastructure.db.tables import events_table


class EventRepository(IEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Event

    async def get_by_id(self, event_id: UUID) -> Event | None:
        query = select(self.model).where(events_table.c.id == event_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: EventStatus | None = None,
        source_rumor_id: UUID | None = None,
    ) -> list[Event]:
        query = select(self.model)
        if status is not None:
            query = query.where(events_table.c.status == status)
        if source_rumor_id is not None:
            query = query.where(events_table.c.source_rumor_id == source_rumor_id)
        query = (
            query.order_by(events_table.c.created_at.desc()).offset(offset).limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, event: Event) -> Event:
        self.session.add(event)
        await self.session.flush()
        return event
