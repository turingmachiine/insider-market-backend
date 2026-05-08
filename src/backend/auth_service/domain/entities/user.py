from datetime import datetime
from typing import Any
from uuid import UUID

from src.backend.auth_service.domain.entities.role import Role


class User:
    """Доменная сущность пользователя."""

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime
    roles: Any

    def __init__(
        self,
        email: str,
        password_hash: str,
        is_active: bool = True,
        roles: list[Role] | None = None,
    ) -> None:
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.roles = roles or []

    def set_active(self, is_active: bool) -> None:
        self.is_active = is_active
