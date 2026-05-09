from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from src.rumor_service.domain.entities import RumorStatus


@dataclass(frozen=True)
class RumorDTO:
    id: UUID
    source_id: UUID
    title: str
    text: str
    normalized_text: str | None
    raw_publication_id: UUID | None
    confidence_score: float
    status: RumorStatus
    tags: list[str]
    event_candidate_payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateRumorDTO:
    source_id: UUID
    title: str
    text: str
    normalized_text: str | None = None
    raw_publication_id: UUID | None = None
    confidence_score: float = 0.0
    status: RumorStatus = RumorStatus.NEW
    tags: list[str] = field(default_factory=list)
    event_candidate_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UpdateRumorStatusDTO:
    status: RumorStatus
