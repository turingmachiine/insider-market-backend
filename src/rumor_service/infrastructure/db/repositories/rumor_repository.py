from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rumor_service.domain.entities import Rumor, RumorStatus
from src.rumor_service.domain.interfaces.repositories import IRumorRepository
from src.rumor_service.infrastructure.db.tables import rumors_table


class RumorRepository(IRumorRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Rumor

    async def get_by_id(self, rumor_id: UUID) -> Rumor | None:
        query = select(self.model).where(rumors_table.c.id == rumor_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: RumorStatus | None = None,
        source_id: UUID | None = None,
        event_id: UUID | None = None,
        is_public: bool | None = None,
    ) -> list[Rumor]:
        query = select(self.model)
        if status is not None:
            query = query.where(rumors_table.c.status == status)
        if source_id is not None:
            query = query.where(rumors_table.c.source_id == source_id)
        if event_id is not None:
            query = query.where(rumors_table.c.event_id == event_id)
        if is_public is not None:
            query = query.where(rumors_table.c.is_public == is_public)
        query = (
            query.order_by(rumors_table.c.created_at.desc()).offset(offset).limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, rumor: Rumor) -> Rumor:
        self.session.add(rumor)
        await self.session.flush()
        return rumor
