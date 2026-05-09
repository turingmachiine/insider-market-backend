from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin_service.domain.entities import SavedFilter
from src.admin_service.domain.interfaces.repositories import ISavedFilterRepository
from src.admin_service.infrastructure.db.tables import saved_filters_table


class SavedFilterRepository(ISavedFilterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = SavedFilter

    async def get_filters(
        self,
        actor_user_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SavedFilter]:
        query = select(self.model).order_by(saved_filters_table.c.created_at.desc())
        if actor_user_id is not None:
            query = query.where(saved_filters_table.c.actor_user_id == actor_user_id)
        result = await self.session.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def count_filters(
        self,
        actor_user_id: UUID | None = None,
    ) -> int:
        query = select(func.count()).select_from(saved_filters_table)
        if actor_user_id is not None:
            query = query.where(saved_filters_table.c.actor_user_id == actor_user_id)
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def save(self, saved_filter: SavedFilter) -> SavedFilter:
        self.session.add(saved_filter)
        await self.session.flush()
        return saved_filter
