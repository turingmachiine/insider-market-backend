from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import UUID

from src.common.domain.security import Permission, normalize_permission


@dataclass(frozen=True)
class UserContext:
    user_id: UUID
    subject: str
    permissions: frozenset[str] = field(default_factory=frozenset)
    roles: frozenset[str] = field(default_factory=frozenset)
    expires_at: int | None = None
    claims: Mapping[str, Any] = field(default_factory=dict)

    def has_permission(self, permission: Permission | str) -> bool:
        return normalize_permission(permission) in self.permissions
