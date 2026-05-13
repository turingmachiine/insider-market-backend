from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth_service.domain.entities import Role, User
from src.auth_service.domain.interfaces.repositories import (
    IPermissionRepository,
    IRoleRepository,
)
from src.auth_service.infrastructure.db.tables import roles_table
from src.common.domain.security import Permission
from src.common.domain.security import Role as AccessRole
from src.common.domain.security import normalize_permission, normalize_role


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

    async def list_all(self) -> list[Role]:
        query = (
            select(self.model)
            .order_by(roles_table.c.name.asc())
            .options(selectinload(Role.permissions))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, name: str) -> Role:
        role = Role(name=name, permissions=[])
        self.session.add(role)
        await self.session.flush()
        return role

    async def ensure_with_permissions(
        self,
        role_name: AccessRole | str,
        permissions: Iterable[Permission | str],
        user: User | None = None,
    ) -> Role:
        role_key = normalize_role(role_name)
        role = await self.get_by_name(role_key)
        if role is None:
            role = Role(name=role_key, permissions=[])
            self.session.add(role)
            await self.session.flush()

        existing = {permission.name for permission in role.permissions}
        for permission_name in permissions:
            normalized_permission = normalize_permission(permission_name)
            if normalized_permission in existing:
                continue
            permission = await self.permission_repository.get_by_name(
                normalized_permission
            )
            if permission is None:
                permission = await self.permission_repository.create(
                    normalized_permission
                )
            role.permissions.append(permission)

        if user is not None and role not in user.roles:
            user.roles.append(role)
        return role

    async def set_permissions(
        self,
        role: Role,
        permissions: Iterable[str],
    ) -> Role:
        next_permissions = []
        for permission_name in permissions:
            permission = await self.permission_repository.get_by_name(permission_name)
            if permission is None:
                permission = await self.permission_repository.create(permission_name)
            next_permissions.append(permission)
        role.permissions = next_permissions
        self.session.add(role)
        await self.session.flush()
        return role
