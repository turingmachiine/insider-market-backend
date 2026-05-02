from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backend.auth_service.domain.entities import Role, User
from src.backend.auth_service.domain.interfaces.repositories import (
    IPermissionRepository,
    IRoleRepository,
)
from src.backend.auth_service.infrastructure.db.tables import roles_table


class RoleRepository(IRoleRepository):
    """Реализация репозитория ролей."""

    def __init__(
        self,
        session: AsyncSession,
        permission_repository: IPermissionRepository,
    ) -> None:
        self.session = session
        self.permission_repository = permission_repository
        self.model = Role

    async def get_by_name(self, name: str) -> Role | None:
        query = (
            select(self.model)
            .where(roles_table.c.name == name)
            .options(selectinload(Role.permissions))
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def ensure_with_permissions(
        self,
        role_name: str,
        permissions: list[str],
        user: User | None = None,
    ) -> Role:
        role = await self.get_by_name(role_name)
        if role is None:
            role = Role(name=role_name, permissions=[])
            self.session.add(role)
            await self.session.flush()

        existing = {permission.name for permission in role.permissions}
        for permission_name in permissions:
            if permission_name in existing:
                continue
            permission = await self.permission_repository.get_by_name(permission_name)
            if permission is None:
                permission = await self.permission_repository.create(permission_name)
            role.permissions.append(permission)

        if user is not None and role not in user.roles:
            user.roles.append(role)
        return role
