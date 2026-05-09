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
from src.auth_service.infrastructure.cache.permissions_cache import PermissionsCache


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        permissions_cache: PermissionsCache,
        settings: AuthSettings,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.permissions_cache = permissions_cache
        self.settings = settings

    async def register(self, email: str, password: str) -> UUID:
        if await self.user_repository.get_by_email(email):
            raise AuthError("User already exists")
        user = await self.user_repository.create(email, hash_password(password))
        await self.role_repository.ensure_with_permissions(
            "user",
            ["nsi:read", "team:write"],
            user=user,
        )
        permissions = self._permissions_for_user(user)
        await self.permissions_cache.set(user.id, permissions)
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
        token = create_access_token(user.id, permissions, self.settings)
        return token, user.id, permissions

    async def get_permissions(self, user_id: UUID) -> list[str]:
        cached = await self.permissions_cache.get(user_id)
        if cached is not None:
            return cached
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise AuthError("User not found")
        permissions = self._permissions_for_user(user)
        await self.permissions_cache.set(user.id, permissions)
        return permissions

    def _permissions_for_user(self, user: User) -> list[str]:
        return sorted(
            {permission.name for role in user.roles for permission in role.permissions}
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
        role_name: str,
        permissions: list[str],
    ) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        await self.role_repository.ensure_with_permissions(
            role_name,
            permissions,
            user=user,
        )
        return user
