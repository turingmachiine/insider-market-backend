from datetime import datetime
from typing import Any
from uuid import UUID

from src.auth_service.domain.entities.role import Role


class User:
    """Доменная сущность пользователя."""

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    failed_login_attempts: int
    locked_until: datetime | None
    password_changed_at: datetime | None
    created_at: datetime
    roles: Any

    def __init__(
        self,
        email: str,
        password_hash: str,
        is_active: bool = True,
        failed_login_attempts: int = 0,
        locked_until: datetime | None = None,
        password_changed_at: datetime | None = None,
        roles: list[Role] | None = None,
    ) -> None:
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
        self.password_changed_at = password_changed_at
        self.roles = roles or []

    def set_active(self, is_active: bool) -> None:
        self.is_active = is_active

    def is_login_locked(self, now: datetime) -> bool:
        return self.locked_until is not None and self.locked_until > now

    def record_failed_login(
        self,
        max_attempts: int,
        lockout_until: datetime,
    ) -> None:
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = lockout_until

    def reset_failed_logins(self) -> None:
        self.failed_login_attempts = 0
        self.locked_until = None

    def set_password_hash(self, password_hash: str, changed_at: datetime) -> None:
        self.password_hash = password_hash
        self.password_changed_at = changed_at
        self.reset_failed_logins()
