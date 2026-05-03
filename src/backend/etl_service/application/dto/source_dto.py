from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class SourceDTO:
    id: UUID
    name: str
    source_type: str
    handle: str | None
    url: str | None
    weight: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
