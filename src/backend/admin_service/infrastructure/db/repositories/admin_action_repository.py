from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.admin_service.domain.entities import AdminAction, AdminActionType
from src.backend.admin_service.domain.interfaces.repositories import (
    IAdminActionRepository,
)
from src.backend.admin_service.infrastructure.db.tables import admin_actions_table


class AdminActionRepository(IAdminActionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = AdminAction

    async def get_actions(
        self,
        limit: int = 100,
        offset: int = 0,
        action_type: AdminActionType | None = None,
        actor_user_id: UUID | None = None,
    ) -> list[AdminAction]:
        query = select(self.model).order_by(admin_actions_table.c.created_at.desc())
        if action_type is not None:
            query = query.where(admin_actions_table.c.action_type == action_type)
        if actor_user_id is not None:
            query = query.where(admin_actions_table.c.actor_user_id == actor_user_id)
        result = await self.session.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def count_actions(
        self,
        action_type: AdminActionType | None = None,
        actor_user_id: UUID | None = None,
    ) -> int:
        query = select(func.count()).select_from(admin_actions_table)
        if action_type is not None:
            query = query.where(admin_actions_table.c.action_type == action_type)
        if actor_user_id is not None:
            query = query.where(admin_actions_table.c.actor_user_id == actor_user_id)
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def save(self, action: AdminAction) -> AdminAction:
        self.session.add(action)
        await self.session.flush()
        return action
