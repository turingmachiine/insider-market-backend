from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from src.auth_service.application.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.entities import AuditAction, AuditLog, RefreshToken, User
from src.auth_service.domain.interfaces.repositories import (
    IAuditLogRepository,
    IRefreshTokenRepository,
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
        refresh_token_repository: IRefreshTokenRepository,
        audit_log_repository: IAuditLogRepository,
        settings: AuthSettings,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.refresh_token_repository = refresh_token_repository
        self.audit_log_repository = audit_log_repository
        self.settings = settings

    async def register(
        self,
        email: str,
        password: str,
        correlation_id: str | None = None,
    ) -> UUID:
        if await self.user_repository.get_by_email(email):
            raise AuthError("User already exists")
        user = await self.user_repository.create(email, hash_password(password))
        user_role = await self.role_repository.get_by_name(Role.USER.value)
        if user_role is None:
            raise AuthError("Default user role is missing")
        if user_role not in user.roles:
            user.roles.append(user_role)
        await self.user_repository.save(user)
        await self._record_audit(
            action=AuditAction.REGISTER,
            target_type="user",
            target_id=str(user.id),
            after={
                "email": user.email,
                "roles": [role.name for role in user.roles],
                "is_active": user.is_active,
            },
            correlation_id=correlation_id,
        )
        return user.id

    async def login(
        self,
        email: str,
        password: str,
        correlation_id: str | None = None,
    ) -> tuple[str, str, UUID, list[str]]:
        user = await self.user_repository.get_by_email(email)
        if (
            user is None
            or not user.is_active
            or not verify_password(password, user.password_hash)
        ):
            raise AuthError("Invalid credentials")
        access_token, refresh_token, permissions = await self._issue_token_pair(user)
        await self._record_audit(
            action=AuditAction.LOGIN,
            actor_user_id=user.id,
            target_type="user",
            target_id=str(user.id),
            after={
                "permissions": permissions,
                "roles": [role.name for role in user.roles],
            },
            correlation_id=correlation_id,
        )
        return access_token, refresh_token, user.id, permissions

    async def refresh(
        self,
        refresh_token: str,
    ) -> tuple[str, str, UUID, list[str]]:
        token_hash = hash_refresh_token(refresh_token)
        stored_token = await self.refresh_token_repository.get_by_token_hash(token_hash)
        now = datetime.now(UTC)
        if stored_token is None:
            raise AuthError("Invalid refresh token")

        user = await self.user_repository.get_by_id(stored_token.user_id)
        if (
            stored_token.revoked_at is not None
            or stored_token.expires_at <= now
            or user is None
            or not user.is_active
        ):
            if user is not None:
                await self.refresh_token_repository.revoke_all_for_user(user.id)
            raise AuthError("Invalid refresh token")

        access_token, new_refresh_token, permissions = await self._issue_token_pair(
            user
        )
        new_token_hash = hash_refresh_token(new_refresh_token)
        new_stored_token = await self.refresh_token_repository.get_by_token_hash(
            new_token_hash,
        )
        stored_token.revoke(now, new_stored_token.id if new_stored_token else None)
        await self.refresh_token_repository.save(stored_token)
        return access_token, new_refresh_token, user.id, permissions

    async def logout(
        self,
        refresh_token: str,
        correlation_id: str | None = None,
    ) -> None:
        token_hash = hash_refresh_token(refresh_token)
        stored_token = await self.refresh_token_repository.get_by_token_hash(token_hash)
        if stored_token is None or stored_token.revoked_at is not None:
            return
        stored_token.revoke(datetime.now(UTC))
        await self.refresh_token_repository.save(stored_token)
        await self._record_audit(
            action=AuditAction.LOGOUT,
            actor_user_id=stored_token.user_id,
            target_type="refresh_token",
            target_id=str(stored_token.id),
            after={
                "user_id": str(stored_token.user_id),
                "revoked_at": (
                    stored_token.revoked_at.isoformat()
                    if stored_token.revoked_at
                    else None
                ),
            },
            correlation_id=correlation_id,
        )

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

    async def set_user_status(
        self,
        user_id: UUID,
        is_active: bool,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        before = {"is_active": user.is_active}
        user.set_active(is_active)
        if not is_active:
            await self.refresh_token_repository.revoke_all_for_user(user.id)
        saved_user = await self.user_repository.save(user)
        await self._record_audit(
            action=AuditAction.USER_STATUS_UPDATE,
            actor_user_id=actor_user_id,
            target_type="user",
            target_id=str(saved_user.id),
            before=before,
            after={"is_active": saved_user.is_active},
            correlation_id=correlation_id,
        )
        return saved_user

    async def assign_role(
        self,
        user_id: UUID,
        role_name: Role | str,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        before = {"roles": sorted(role.name for role in user.roles)}
        role = await self.role_repository.get_by_name(Role(role_name).value)
        if role is None:
            raise AuthError(f"Role {Role(role_name).value} is missing")
        if role not in user.roles:
            user.roles.append(role)
        saved_user = await self.user_repository.save(user)
        await self.refresh_token_repository.revoke_all_for_user(user.id)
        await self._record_audit(
            action=AuditAction.ROLE_ASSIGNMENT,
            actor_user_id=actor_user_id,
            target_type="user",
            target_id=str(saved_user.id),
            before=before,
            after={"roles": sorted(role.name for role in saved_user.roles)},
            correlation_id=correlation_id,
        )
        return saved_user

    async def revoke_user_tokens(
        self,
        user_id: UUID,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        await self.refresh_token_repository.revoke_all_for_user(user.id)
        await self._record_audit(
            action=AuditAction.TOKENS_REVOKE,
            actor_user_id=actor_user_id,
            target_type="user",
            target_id=str(user.id),
            after={"tokens_revoked": True},
            correlation_id=correlation_id,
        )
        return user

    async def _issue_token_pair(self, user: User) -> tuple[str, str, list[str]]:
        permissions = self._permissions_for_user(user)
        access_token = create_access_token(
            user.id,
            permissions,
            self.settings,
            roles=[role.name for role in user.roles],
        )
        refresh_token = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(
            seconds=self.settings.REFRESH_TOKEN_TTL
        )
        await self.refresh_token_repository.save(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_refresh_token(refresh_token),
                expires_at=expires_at,
            ),
        )
        return access_token, refresh_token, permissions

    async def _record_audit(
        self,
        action: AuditAction,
        target_type: str,
        target_id: str | None = None,
        *,
        actor_user_id: UUID | None = None,
        before: dict | None = None,
        after: dict | None = None,
        correlation_id: str | None = None,
    ) -> None:
        await self.audit_log_repository.save(
            AuditLog(
                id=uuid4(),
                actor_user_id=actor_user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                before=before,
                after=after,
                correlation_id=correlation_id,
            )
        )
