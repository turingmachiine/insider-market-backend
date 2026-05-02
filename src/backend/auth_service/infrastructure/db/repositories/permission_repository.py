from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.auth_service.domain.entities import Permission
from src.backend.auth_service.domain.interfaces.repositories import (
    IPermissionRepository,
)
from src.backend.auth_service.infrastructure.db.tables import permissions_table


class PermissionRepository(IPermissionRepository):
    """Реализация репозитория permissions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = Permission

    async def get_by_name(self, name: str) -> Permission | None:
        query = select(self.model).where(permissions_table.c.name == name)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def create(self, name: str) -> Permission:
        permission = Permission(name=name)
        self.session.add(permission)
        await self.session.flush()
        return permission
