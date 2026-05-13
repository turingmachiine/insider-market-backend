from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_service.domain.entities import Permission
from src.auth_service.domain.interfaces.repositories import IPermissionRepository
from src.auth_service.infrastructure.db.tables import permissions_table


class PermissionRepository(IPermissionRepository):
    """Реализация репозитория permissions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = Permission

    async def get_by_name(self, name: str) -> Permission | None:
        query = select(self.model).where(permissions_table.c.name == name)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def list_all(self) -> list[Permission]:
        query = select(self.model).order_by(permissions_table.c.name.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, name: str) -> Permission:
        permission = Permission(name=name)
        self.session.add(permission)
        await self.session.flush()
        return permission
