from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.rumor_service.domain.entities import Source
from src.backend.rumor_service.domain.interfaces.repositories import ISourceRepository
from src.backend.rumor_service.infrastructure.db.tables import sources_table


class SourceRepository(ISourceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Source

    async def get_by_id(self, source_id: UUID) -> Source | None:
        query = select(self.model).where(sources_table.c.id == source_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_name(self, name: str) -> Source | None:
        query = select(self.model).where(sources_table.c.name == name)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
    ) -> list[Source]:
        query = select(self.model).offset(offset).limit(limit)
        if active_only:
            query = query.where(sources_table.c.is_active.is_(True))
        query = query.order_by(sources_table.c.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, source: Source) -> Source:
        self.session.add(source)
        await self.session.flush()
        return source
