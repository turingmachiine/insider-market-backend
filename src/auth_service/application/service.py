from uuid import UUID

from src.auth_service.application.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.entities import User
from src.auth_service.domain.interfaces.repositories import (
    IRoleRepository,
    IUserRepository,
)
from src.common.domain.security import ROLE_PERMISSIONS, Role


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        settings: AuthSettings,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.settings = settings

    async def register(self, email: str, password: str) -> UUID:
        if await self.user_repository.get_by_email(email):
            raise AuthError("User already exists")
        user = await self.user_repository.create(email, hash_password(password))
        user_role = await self.role_repository.get_by_name(Role.USER.value)
        if user_role is None:
            raise AuthError("Default user role is missing")
        if user_role not in user.roles:
            user.roles.append(user_role)
        await self.user_repository.save(user)
        return user.id

    async def login(self, email: str, password: str) -> tuple[str, UUID, list[str]]:
        user = await self.user_repository.get_by_email(email)
        if (
            user is None
            or not user.is_active
            or not verify_password(password, user.password_hash)
        ):
            raise AuthError("Invalid credentials")
        permissions = await self.get_permissions(user.id)
        token = create_access_token(
            user.id,
            permissions,
            self.settings,
            roles=[role.name for role in user.roles],
        )
        return token, user.id, permissions

    async def get_permissions(self, user_id: UUID) -> list[str]:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise AuthError("User not found")
        return self._permissions_for_user(user)

    def _permissions_for_user(self, user: User) -> list[str]:
        return sorted(
            {permission.name for role in user.roles for permission in role.permissions}
        )

    async def bootstrap_access_control(self) -> None:
        for role, permissions in ROLE_PERMISSIONS.items():
            await self.role_repository.ensure_with_permissions(role, permissions)

        users = await self.user_repository.get_all(limit=10_000, offset=0)
        for user in users:
            if not user.roles:
                await self.role_repository.ensure_with_permissions(
                    Role.USER,
                    ROLE_PERMISSIONS[Role.USER],
                    user=user,
                )

    async def list_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        return await self.user_repository.get_all(limit=limit, offset=offset)

    async def count_users(self) -> int:
        return await self.user_repository.count_all()

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def set_user_status(self, user_id: UUID, is_active: bool) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        user.set_active(is_active)
        return await self.user_repository.save(user)

    async def assign_role(
        self,
        user_id: UUID,
        role_name: Role | str,
    ) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        role = await self.role_repository.get_by_name(Role(role_name).value)
        if role is None:
            raise AuthError(f"Role {Role(role_name).value} is missing")
        if role not in user.roles:
            user.roles.append(role)
        await self.user_repository.save(user)
        return user
