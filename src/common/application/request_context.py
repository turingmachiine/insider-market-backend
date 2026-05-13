from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class RequestContext:
    correlation_id: str | None = None
    user_id: UUID | None = None
    service_name: str | None = None


class RequestContextProvider(Protocol):
    def get_context(self) -> RequestContext:
        raise NotImplementedError


__all__ = ["RequestContext", "RequestContextProvider"]
