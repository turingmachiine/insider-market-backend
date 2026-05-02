from uuid import UUID

from src.backend.auth_service.application.repository import AuthRepository
from src.backend.auth_service.application.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from src.backend.auth_service.core.config import AuthSettings
from src.backend.auth_service.infrastructure.cache.permissions_cache import (
    PermissionsCache,
)


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(
        self,
        repository: AuthRepository,
        permissions_cache: PermissionsCache,
        settings: AuthSettings,
    ) -> None:
        self.repository = repository
        self.permissions_cache = permissions_cache
        self.settings = settings

    async def register(self, email: str, password: str) -> UUID:
        if await self.repository.get_user_by_email(email):
            raise AuthError("User already exists")
        user = await self.repository.create_user(email, hash_password(password))
        permissions = self.repository.permissions_for_user(user)
        await self.permissions_cache.set(user.id, permissions)
        return user.id

    async def login(self, email: str, password: str) -> tuple[str, UUID, list[str]]:
        user = await self.repository.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Invalid credentials")
        permissions = await self.get_permissions(user.id)
        token = create_access_token(user.id, permissions, self.settings)
        return token, user.id, permissions

    async def get_permissions(self, user_id: UUID) -> list[str]:
        cached = await self.permissions_cache.get(user_id)
        if cached is not None:
            return cached
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise AuthError("User not found")
        permissions = self.repository.permissions_for_user(user)
        await self.permissions_cache.set(user.id, permissions)
        return permissions
