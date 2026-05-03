from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class CreateRumorDTO:
    source_id: UUID
    title: str
    text: str
    normalized_text: str | None
    raw_publication_id: UUID
    confidence_score: float
    status: str = "candidate"
    tags: list[str] = field(default_factory=list)
    event_candidate_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RumorDTO:
    id: UUID
    source_id: UUID
    title: str
    text: str
    normalized_text: str | None
    raw_publication_id: UUID | None
    confidence_score: float
    status: str
    tags: list[str]
    event_candidate_payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime
