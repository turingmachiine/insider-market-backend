from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.auth_service.application.security import (
    decode_access_token,
    hash_refresh_token,
)
from src.auth_service.application.service import AuthError, AuthService
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.entities import (
    AuditAction,
    AuditLog,
    PasswordResetToken,
    Permission,
    RefreshToken,
    Role,
    User,
)
from src.auth_service.domain.interfaces.repositories import (
    IAuditLogRepository,
    IPasswordResetTokenRepository,
    IPermissionRepository,
    IRefreshTokenRepository,
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

    async def list_all(self) -> list[Role]:
        return sorted(self.roles.values(), key=lambda role: role.name)

    async def create(self, name: str) -> Role:
        role = Role(name=name, permissions=[])
        self.roles[name] = role
        return role

    async def ensure_with_permissions(
        self,
        role_name: AccessRole | str,
        permissions: Iterable[AccessPermission | str],
        user: User | None = None,
    ) -> Role:
        raise AssertionError("bootstrap-only path should not be used in this test")

    async def set_permissions(
        self,
        role: Role,
        permissions: Iterable[str],
    ) -> Role:
        role.permissions = [Permission(name=permission) for permission in permissions]
        return role


class FakePermissionRepository(IPermissionRepository):
    def __init__(self, permissions: dict[str, Permission] | None = None) -> None:
        self.permissions = permissions or {}

    async def get_by_name(self, name: str) -> Permission | None:
        return self.permissions.get(name)

    async def list_all(self) -> list[Permission]:
        return sorted(self.permissions.values(), key=lambda permission: permission.name)

    async def create(self, name: str) -> Permission:
        permission = Permission(name=name)
        self.permissions[name] = permission
        return permission


class FakeRefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self) -> None:
        self.tokens_by_hash: dict[str, RefreshToken] = {}

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        return self.tokens_by_hash.get(token_hash)

    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.id = uuid4()
        self.tokens_by_hash[refresh_token.token_hash] = refresh_token
        return refresh_token

    async def revoke_all_for_user(self, user_id: object) -> None:
        now = datetime.now(UTC)
        for refresh_token in self.tokens_by_hash.values():
            if refresh_token.user_id == user_id and refresh_token.revoked_at is None:
                refresh_token.revoke(now)

    async def revoke_all_for_roles(self, role_names: list[str]) -> None:
        now = datetime.now(UTC)
        for refresh_token in self.tokens_by_hash.values():
            if refresh_token.revoked_at is None:
                refresh_token.revoke(now)


class FakePasswordResetTokenRepository(IPasswordResetTokenRepository):
    def __init__(self) -> None:
        self.tokens_by_hash: dict[str, PasswordResetToken] = {}

    async def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        return self.tokens_by_hash.get(token_hash)

    async def save(
        self, password_reset_token: PasswordResetToken
    ) -> PasswordResetToken:
        password_reset_token.id = uuid4()
        self.tokens_by_hash[password_reset_token.token_hash] = password_reset_token
        return password_reset_token

    async def revoke_all_for_user(self, user_id: object) -> None:
        now = datetime.now(UTC)
        for token in self.tokens_by_hash.values():
            if token.user_id == user_id and token.used_at is None:
                token.mark_used(now)


class FakeAuditLogRepository(IAuditLogRepository):
    def __init__(self) -> None:
        self.logs: list[AuditLog] = []

    async def save(self, audit_log: AuditLog) -> AuditLog:
        self.logs.append(audit_log)
        return audit_log

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        action: AuditAction | None = None,
        actor_user_id: UUID | None = None,
    ) -> list[AuditLog]:
        logs = self.logs
        if action is not None:
            logs = [log for log in logs if log.action == action]
        if actor_user_id is not None:
            logs = [log for log in logs if log.actor_user_id == actor_user_id]
        return logs[offset : offset + limit]

    async def count_all(
        self,
        action: AuditAction | None = None,
        actor_user_id: UUID | None = None,
    ) -> int:
        return len(
            await self.get_all(
                limit=len(self.logs),
                action=action,
                actor_user_id=actor_user_id,
            )
        )


@pytest.mark.asyncio
async def test_login_uses_permissions_from_database_relations() -> None:
    custom_permission = Permission(name="catalog:read")
    user_role = Role(name="user", permissions=[custom_permission])
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({"user": user_role})
    refresh_token_repo = FakeRefreshTokenRepository()
    password_reset_token_repo = FakePasswordResetTokenRepository()
    audit_log_repo = FakeAuditLogRepository()
    settings = AuthSettings(
        JWT_SECRET="secret",
        JWT_ALGORITHM="HS256",
        JWT_TTL=3600,
        REFRESH_TOKEN_TTL=3600,
    )
    service = AuthService(
        user_repo,
        role_repo,
        FakePermissionRepository(),
        refresh_token_repo,
        password_reset_token_repo,
        audit_log_repo,
        settings,
    )

    await service.register(
        "alice@example.com",
        "Password123!",
        correlation_id="request-1",
    )
    token, refresh_token, user_id, permissions = await service.login(
        "alice@example.com",
        "Password123!",
        correlation_id="request-2",
    )
    claims = decode_access_token(token, settings)

    assert user_id is not None
    assert refresh_token
    assert permissions == ["catalog:read"]
    assert claims["permissions"] == ["catalog:read"]
    assert claims["iat"]
    assert [log.action for log in audit_log_repo.logs] == [
        AuditAction.REGISTER,
        AuditAction.LOGIN,
    ]
    assert audit_log_repo.logs[0].correlation_id == "request-1"
    assert audit_log_repo.logs[1].actor_user_id == user_id
    assert audit_log_repo.logs[1].correlation_id == "request-2"


@pytest.mark.asyncio
async def test_refresh_rotates_refresh_token() -> None:
    user_role = Role(name="user", permissions=[Permission(name="catalog:read")])
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({"user": user_role})
    refresh_token_repo = FakeRefreshTokenRepository()
    password_reset_token_repo = FakePasswordResetTokenRepository()
    audit_log_repo = FakeAuditLogRepository()
    settings = AuthSettings(
        JWT_SECRET="secret",
        JWT_ALGORITHM="HS256",
        JWT_TTL=3600,
        REFRESH_TOKEN_TTL=3600,
    )
    service = AuthService(
        user_repo,
        role_repo,
        FakePermissionRepository(),
        refresh_token_repo,
        password_reset_token_repo,
        audit_log_repo,
        settings,
    )

    await service.register("alice@example.com", "Password123!")
    _, old_refresh_token, _, _ = await service.login(
        "alice@example.com",
        "Password123!",
    )
    access_token, new_refresh_token, user_id, permissions = await service.refresh(
        old_refresh_token,
    )

    old_stored_token = await refresh_token_repo.get_by_token_hash(
        hash_refresh_token(old_refresh_token),
    )
    claims = decode_access_token(access_token, settings)
    assert new_refresh_token != old_refresh_token
    assert old_stored_token is not None
    assert old_stored_token.revoked_at is not None
    assert old_stored_token.replaced_by_token_id is not None
    assert claims["sub"] == str(user_id)
    assert permissions == ["catalog:read"]


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token() -> None:
    user_role = Role(name="user", permissions=[Permission(name="catalog:read")])
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({"user": user_role})
    refresh_token_repo = FakeRefreshTokenRepository()
    password_reset_token_repo = FakePasswordResetTokenRepository()
    audit_log_repo = FakeAuditLogRepository()
    settings = AuthSettings(
        JWT_SECRET="secret",
        JWT_ALGORITHM="HS256",
        JWT_TTL=3600,
        REFRESH_TOKEN_TTL=3600,
    )
    service = AuthService(
        user_repo,
        role_repo,
        FakePermissionRepository(),
        refresh_token_repo,
        password_reset_token_repo,
        audit_log_repo,
        settings,
    )

    await service.register("alice@example.com", "Password123!")
    _, refresh_token, _, _ = await service.login("alice@example.com", "Password123!")
    await service.logout(refresh_token, correlation_id="request-3")

    stored_token = await refresh_token_repo.get_by_token_hash(
        hash_refresh_token(refresh_token),
    )
    assert stored_token is not None
    assert stored_token.revoked_at is not None
    assert audit_log_repo.logs[-1].action == AuditAction.LOGOUT
    assert audit_log_repo.logs[-1].target_id == str(stored_token.id)
    assert audit_log_repo.logs[-1].correlation_id == "request-3"


@pytest.mark.asyncio
async def test_register_rejects_weak_password() -> None:
    user_role = Role(name="user", permissions=[Permission(name="catalog:read")])
    service = AuthService(
        FakeUserRepository(),
        FakeRoleRepository({"user": user_role}),
        FakePermissionRepository(),
        FakeRefreshTokenRepository(),
        FakePasswordResetTokenRepository(),
        FakeAuditLogRepository(),
        AuthSettings(JWT_SECRET="secret"),
    )

    with pytest.raises(AuthError, match="at least 12"):
        await service.register("alice@example.com", "password")


@pytest.mark.asyncio
async def test_failed_logins_lock_user_temporarily() -> None:
    user_role = Role(name="user", permissions=[Permission(name="catalog:read")])
    user_repo = FakeUserRepository()
    service = AuthService(
        user_repo,
        FakeRoleRepository({"user": user_role}),
        FakePermissionRepository(),
        FakeRefreshTokenRepository(),
        FakePasswordResetTokenRepository(),
        FakeAuditLogRepository(),
        AuthSettings(
            JWT_SECRET="secret",
            MAX_FAILED_LOGIN_ATTEMPTS=2,
            LOGIN_LOCKOUT_SECONDS=60,
        ),
    )

    await service.register("alice@example.com", "Password123!")
    with pytest.raises(AuthError):
        await service.login("alice@example.com", "WrongPassword123!")
    with pytest.raises(AuthError):
        await service.login("alice@example.com", "WrongPassword123!")

    user = await user_repo.get_by_email("alice@example.com")
    assert user is not None
    assert user.failed_login_attempts == 2
    assert user.locked_until is not None
    with pytest.raises(AuthError):
        await service.login("alice@example.com", "Password123!")


@pytest.mark.asyncio
async def test_password_reset_changes_password_and_revokes_tokens() -> None:
    user_role = Role(name="user", permissions=[Permission(name="catalog:read")])
    refresh_token_repo = FakeRefreshTokenRepository()
    password_reset_token_repo = FakePasswordResetTokenRepository()
    audit_log_repo = FakeAuditLogRepository()
    service = AuthService(
        FakeUserRepository(),
        FakeRoleRepository({"user": user_role}),
        FakePermissionRepository(),
        refresh_token_repo,
        password_reset_token_repo,
        audit_log_repo,
        AuthSettings(JWT_SECRET="secret"),
    )

    await service.register("alice@example.com", "Password123!")
    _, refresh_token, user_id, _ = await service.login(
        "alice@example.com",
        "Password123!",
    )
    reset_token = await service.request_password_reset("alice@example.com")
    assert reset_token is not None

    changed_user_id = await service.reset_password(reset_token, "NewPassword123!")
    old_stored_token = await refresh_token_repo.get_by_token_hash(
        hash_refresh_token(refresh_token)
    )

    assert changed_user_id == user_id
    assert old_stored_token is not None
    assert old_stored_token.revoked_at is not None
    with pytest.raises(AuthError):
        await service.login("alice@example.com", "Password123!")
    _, new_refresh_token, _, _ = await service.login(
        "alice@example.com",
        "NewPassword123!",
    )
    assert new_refresh_token
    assert audit_log_repo.logs[-1].action == AuditAction.LOGIN
