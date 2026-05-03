from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class CreateRawPublicationDTO:
    source_id: UUID
    text: str
    external_id: str | None = None
    url: str | None = None
    published_at: datetime | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RawPublicationDTO:
    id: UUID
    source_id: UUID
    text: str
    external_id: str | None
    url: str | None
    published_at: datetime | None
    collected_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
