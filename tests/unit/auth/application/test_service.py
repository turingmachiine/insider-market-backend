from collections.abc import Iterable
from uuid import uuid4

import pytest

from src.auth_service.application.security import decode_access_token
from src.auth_service.application.service import AuthService
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.entities import Permission, Role, User
from src.auth_service.domain.interfaces.repositories import (
    IRoleRepository,
    IUserRepository,
)
from src.common.domain.security import Permission as AccessPermission
from src.common.domain.security import Role as AccessRole


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self.users_by_email: dict[str, User] = {}
        self.users_by_id: dict[object, User] = {}

    async def get_by_email(self, email: str) -> User | None:
        return self.users_by_email.get(email)

    async def get_by_id(self, user_id: object) -> User | None:
        return self.users_by_id.get(user_id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        return list(self.users_by_email.values())[offset : offset + limit]

    async def count_all(self) -> int:
        return len(self.users_by_email)

    async def create(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash, roles=[])
        user.id = uuid4()
        self.users_by_email[email] = user
        self.users_by_id[user.id] = user
        return user

    async def save(self, user: User) -> User:
        self.users_by_email[user.email] = user
        self.users_by_id[user.id] = user
        return user


class FakeRoleRepository(IRoleRepository):
    def __init__(self, roles: dict[str, Role]) -> None:
        self.roles = roles

    async def get_by_name(self, name: str) -> Role | None:
        return self.roles.get(name)

    async def ensure_with_permissions(
        self,
        role_name: AccessRole | str,
        permissions: Iterable[AccessPermission | str],
        user: User | None = None,
    ) -> Role:
        raise AssertionError("bootstrap-only path should not be used in this test")


@pytest.mark.asyncio
async def test_login_uses_permissions_from_database_relations() -> None:
    custom_permission = Permission(name="catalog:read")
    user_role = Role(name="user", permissions=[custom_permission])
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({"user": user_role})
    settings = AuthSettings(
        JWT_SECRET="secret",
        JWT_ALGORITHM="HS256",
        JWT_TTL=3600,
    )
    service = AuthService(user_repo, role_repo, settings)

    await service.register("alice@example.com", "password")
    token, user_id, permissions = await service.login("alice@example.com", "password")
    claims = decode_access_token(token, settings)

    assert user_id is not None
    assert permissions == ["catalog:read"]
    assert claims["permissions"] == ["catalog:read"]
