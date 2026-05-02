from typing import Any
from uuid import UUID

from src.backend.auth_service.domain.entities.permission import Permission


class Role:
    """Доменная сущность роли."""

    id: UUID
    name: str
    users: Any
    permissions: Any

    def __init__(
        self,
        name: str,
        permissions: list[Permission] | None = None,
    ) -> None:
        self.name = name
        self.permissions = permissions or []
