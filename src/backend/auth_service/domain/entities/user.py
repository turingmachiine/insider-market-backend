from datetime import datetime
from typing import Any
from uuid import UUID

from src.backend.auth_service.domain.entities.role import Role


class User:
    """Доменная сущность пользователя."""

    id: UUID
    email: str
    password_hash: str
    created_at: datetime
    roles: Any

    def __init__(
        self,
        email: str,
        password_hash: str,
        roles: list[Role] | None = None,
    ) -> None:
        self.email = email
        self.password_hash = password_hash
        self.roles = roles or []
