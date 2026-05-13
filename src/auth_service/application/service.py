import re
from datetime import UTC, datetime, timedelta
from typing import TypedDict
from uuid import UUID, uuid4

from src.auth_service.application.constants import ACCESS_CONTROL_NAME_PATTERN
from src.auth_service.application.password_policy import (
    PasswordPolicyError,
    validate_password_policy,
)
from src.auth_service.application.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    password_hash_needs_update,
    verify_password,
)
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.entities import (
    AuditAction,
    AuditLog,
    PasswordResetToken,
    RefreshToken,
)
from src.auth_service.domain.entities import Role as AuthRole
from src.auth_service.domain.entities import User
from src.auth_service.domain.interfaces.repositories import (
    IAuditLogRepository,
    IPasswordResetTokenRepository,
    IPermissionRepository,
    IRefreshTokenRepository,
    IRoleRepository,
    IUserRepository,
)
from src.common.domain.security import Role


class AuthError(ValueError):
    pass


INVALID_CREDENTIALS_MESSAGE = "Invalid credentials"


class RolePayload(TypedDict):
    name: str
    permissions: list[str]


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
        refresh_token_repository: IRefreshTokenRepository,
        password_reset_token_repository: IPasswordResetTokenRepository,
        audit_log_repository: IAuditLogRepository,
        settings: AuthSettings,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.permission_repository = permission_repository
        self.refresh_token_repository = refresh_token_repository
        self.password_reset_token_repository = password_reset_token_repository
        self.audit_log_repository = audit_log_repository
        self.settings = settings
        self._access_control_name_pattern = re.compile(ACCESS_CONTROL_NAME_PATTERN)

    async def register(
        self,
        email: str,
        password: str,
        correlation_id: str | None = None,
    ) -> UUID:
        if await self.user_repository.get_by_email(email):
            raise AuthError("User already exists")
        self._validate_password(password)
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
        now = datetime.now(UTC)
        if user is None or not user.is_active:
            raise AuthError()
        if user.is_login_locked(now):
            raise AuthError(INVALID_CREDENTIALS_MESSAGE)
        if not verify_password(password, user.password_hash):
            user.record_failed_login(
                self.settings.MAX_FAILED_LOGIN_ATTEMPTS,
                now + timedelta(seconds=self.settings.LOGIN_LOCKOUT_SECONDS),
            )
            await self.user_repository.save(user)
            raise AuthError(INVALID_CREDENTIALS_MESSAGE)
        password_needs_update = password_hash_needs_update(user.password_hash)
        user.reset_failed_logins()
        if password_needs_update:
            user.set_password_hash(hash_password(password), now)
        await self.user_repository.save(user)
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

    async def request_password_reset(
        self,
        email: str,
        correlation_id: str | None = None,
    ) -> str | None:
        user = await self.user_repository.get_by_email(email)
        if user is None or not user.is_active:
            return None

        await self.password_reset_token_repository.revoke_all_for_user(user.id)
        raw_token = create_refresh_token()
        token = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC)
            + timedelta(seconds=self.settings.PASSWORD_RESET_TOKEN_TTL),
        )
        await self.password_reset_token_repository.save(token)
        await self._record_audit(
            action=AuditAction.PASSWORD_RESET_REQUEST,
            target_type="user",
            target_id=str(user.id),
            after={"email": user.email},
            correlation_id=correlation_id,
        )
        return raw_token

    async def reset_password(
        self,
        reset_token: str,
        new_password: str,
        correlation_id: str | None = None,
    ) -> UUID:
        self._validate_password(new_password)
        token_hash = hash_refresh_token(reset_token)
        stored_token = await self.password_reset_token_repository.get_by_token_hash(
            token_hash
        )
        now = datetime.now(UTC)
        if stored_token is None or not stored_token.is_usable(now):
            raise AuthError("Invalid password reset token")

        user = await self.user_repository.get_by_id(stored_token.user_id)
        if user is None or not user.is_active:
            raise AuthError("Invalid password reset token")

        user.set_password_hash(hash_password(new_password), now)
        stored_token.mark_used(now)
        await self.user_repository.save(user)
        await self.password_reset_token_repository.save(stored_token)
        await self.refresh_token_repository.revoke_all_for_user(user.id)
        await self._record_audit(
            action=AuditAction.PASSWORD_RESET,
            target_type="user",
            target_id=str(user.id),
            after={"tokens_revoked": True},
            correlation_id=correlation_id,
        )
        return user.id

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
        correlation_id: str | None = None,
    ) -> None:
        self._validate_password(new_password)
        user = await self.user_repository.get_by_id(user_id)
        if (
            user is None
            or not user.is_active
            or not verify_password(current_password, user.password_hash)
        ):
            raise AuthError(INVALID_CREDENTIALS_MESSAGE)
        if verify_password(new_password, user.password_hash):
            raise AuthError("New password must differ from current password")

        user.set_password_hash(hash_password(new_password), datetime.now(UTC))
        await self.user_repository.save(user)
        await self.refresh_token_repository.revoke_all_for_user(user.id)
        await self.password_reset_token_repository.revoke_all_for_user(user.id)
        await self._record_audit(
            action=AuditAction.PASSWORD_CHANGE,
            actor_user_id=user.id,
            target_type="user",
            target_id=str(user.id),
            after={"tokens_revoked": True},
            correlation_id=correlation_id,
        )

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
        users = await self.user_repository.get_all(limit=10_000, offset=0)
        user_role = await self.role_repository.get_by_name(Role.USER.value)
        if user_role is None:
            raise AuthError("Default user role is missing")
        for user in users:
            if not user.roles:
                user.roles.append(user_role)
                await self.user_repository.save(user)

    async def list_permissions(self) -> list[str]:
        permissions = await self.permission_repository.list_all()
        return [permission.name for permission in permissions]

    async def create_permission(
        self,
        name: str,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> str:
        permission_name = self._normalize_access_control_name(name, "Permission")
        existing = await self.permission_repository.get_by_name(permission_name)
        if existing is not None:
            raise AuthError(f"Permission {permission_name} already exists")
        permission = await self.permission_repository.create(permission_name)
        await self._record_audit(
            action=AuditAction.PERMISSION_CREATE,
            actor_user_id=actor_user_id,
            target_type="permission",
            target_id=permission.name,
            after={"name": permission.name},
            correlation_id=correlation_id,
        )
        return permission.name

    async def list_roles(self) -> list[RolePayload]:
        roles = await self.role_repository.list_all()
        return [
            {
                "name": role.name,
                "permissions": sorted(
                    permission.name for permission in role.permissions
                ),
            }
            for role in roles
        ]

    async def create_role(
        self,
        name: str,
        permissions: list[str] | None = None,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> RolePayload:
        role_name = self._normalize_access_control_name(name, "Role")
        permission_names = self._normalize_permission_names(permissions or [])
        existing = await self.role_repository.get_by_name(role_name)
        if existing is not None:
            raise AuthError(f"Role {role_name} already exists")
        role = await self.role_repository.create(role_name)
        if permission_names:
            role = await self.role_repository.set_permissions(role, permission_names)
        result = self._role_payload(role)
        await self._record_audit(
            action=AuditAction.ROLE_CREATE,
            actor_user_id=actor_user_id,
            target_type="role",
            target_id=role.name,
            after=dict(result),
            correlation_id=correlation_id,
        )
        return result

    async def set_role_permissions(
        self,
        role_name: str,
        permissions: list[str],
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> RolePayload:
        normalized_role_name = self._normalize_access_control_name(role_name, "Role")
        permission_names = self._normalize_permission_names(permissions)
        role = await self.role_repository.get_by_name(normalized_role_name)
        if role is None:
            raise AuthError(f"Role {normalized_role_name} not found")
        before = self._role_payload(role)
        role = await self.role_repository.set_permissions(role, permission_names)
        await self.refresh_token_repository.revoke_all_for_roles([role.name])
        after = self._role_payload(role)
        await self._record_audit(
            action=AuditAction.ROLE_PERMISSIONS_UPDATE,
            actor_user_id=actor_user_id,
            target_type="role",
            target_id=role.name,
            before=dict(before),
            after=dict(after),
            correlation_id=correlation_id,
        )
        return after

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
        normalized_role_name = self._normalize_access_control_name(
            str(role_name), "Role"
        )
        role = await self.role_repository.get_by_name(normalized_role_name)
        if role is None:
            raise AuthError(f"Role {normalized_role_name} is missing")
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

    async def revoke_role(
        self,
        user_id: UUID,
        role_name: str,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None
        normalized_role_name = self._normalize_access_control_name(role_name, "Role")
        before = {"roles": sorted(role.name for role in user.roles)}
        user.roles = [role for role in user.roles if role.name != normalized_role_name]
        saved_user = await self.user_repository.save(user)
        await self.refresh_token_repository.revoke_all_for_user(user.id)
        await self._record_audit(
            action=AuditAction.ROLE_REVOCATION,
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

    def _validate_password(self, password: str) -> None:
        try:
            validate_password_policy(password)
        except PasswordPolicyError as exc:
            raise AuthError(str(exc)) from exc

    def _normalize_access_control_name(self, name: str, label: str) -> str:
        normalized = name.strip().lower()
        if not self._access_control_name_pattern.fullmatch(normalized):
            raise AuthError(f"{label} name is invalid")
        return normalized

    def _normalize_permission_names(self, permissions: list[str]) -> list[str]:
        return sorted(
            {
                self._normalize_access_control_name(permission, "Permission")
                for permission in permissions
            }
        )

    @staticmethod
    def _role_payload(role: AuthRole) -> RolePayload:
        return {
            "name": role.name,
            "permissions": sorted(permission.name for permission in role.permissions),
        }

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
