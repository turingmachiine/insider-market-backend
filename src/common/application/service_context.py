from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ServiceContext:
    service_name: str
    audience: str
    scopes: frozenset[str] = field(default_factory=frozenset)
    expires_at: int | None = None
    claims: Mapping[str, Any] = field(default_factory=dict)

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes
