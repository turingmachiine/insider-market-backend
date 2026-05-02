from typing import Any
from uuid import UUID


class Permission:
    """Доменная сущность permission."""

    id: UUID
    name: str
    roles: Any

    def __init__(self, name: str) -> None:
        self.name = name
