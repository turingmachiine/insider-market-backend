from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backend.auth_service.infrastructure.db.models import Permission, Role, User


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash, roles=[])
        self.session.add(user)
        await self.session.flush()
        await self.ensure_role_with_permissions(
            "user",
            ["nsi:read", "team:write"],
            user=user,
        )
        await self.session.flush()
        return user

    async def ensure_role_with_permissions(
        self,
        role_name: str,
        permissions: list[str],
        user: User | None = None,
    ) -> Role:
        role = await self._get_role(role_name)
        if role is None:
            role = Role(name=role_name, permissions=[])
            self.session.add(role)
            await self.session.flush()

        existing = {permission.name for permission in role.permissions}
        for permission_name in permissions:
            if permission_name in existing:
                continue
            permission = await self._get_permission(permission_name)
            if permission is None:
                permission = Permission(name=permission_name)
                self.session.add(permission)
                await self.session.flush()
            role.permissions.append(permission)

        if user is not None and role not in user.roles:
            user.roles.append(role)
        return role

    def permissions_for_user(self, user: User) -> list[str]:
        return sorted(
            {permission.name for role in user.roles for permission in role.permissions}
        )

    async def _get_role(self, name: str) -> Role | None:
        result = await self.session.execute(
            select(Role)
            .where(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()

    async def _get_permission(self, name: str) -> Permission | None:
        result = await self.session.execute(
            select(Permission).where(Permission.name == name)
        )
        return result.scalar_one_or_none()
