from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.rumor_service.domain.entities import RawPublication
from src.backend.rumor_service.domain.interfaces.repositories import (
    IRawPublicationRepository,
)
from src.backend.rumor_service.infrastructure.db.tables import raw_publications_table


class RawPublicationRepository(IRawPublicationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = RawPublication

    async def get_by_id(self, publication_id: UUID) -> RawPublication | None:
        query = select(self.model).where(raw_publications_table.c.id == publication_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_external_id(
        self,
        source_id: UUID,
        external_id: str,
    ) -> RawPublication | None:
        query = select(self.model).where(
            raw_publications_table.c.source_id == source_id,
            raw_publications_table.c.external_id == external_id,
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_source(
        self,
        source_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RawPublication]:
        query = (
            select(self.model)
            .where(raw_publications_table.c.source_id == source_id)
            .order_by(raw_publications_table.c.published_at.desc().nullslast())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, publication: RawPublication) -> RawPublication:
        self.session.add(publication)
        await self.session.flush()
        return publication
