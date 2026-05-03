from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.backend.rumor_service.domain.entities import SourceType


@dataclass(frozen=True)
class SourceDTO:
    id: UUID
    name: str
    source_type: SourceType
    handle: str | None
    url: str | None
    weight: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateSourceDTO:
    name: str
    source_type: SourceType
    handle: str | None = None
    url: str | None = None
    weight: float = 1.0
    is_active: bool = True
