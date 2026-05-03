from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class NormalizedRumorCandidate:
    source_id: UUID
    title: str
    text: str
    normalized_text: str
    raw_publication_id: UUID
    confidence_score: float
    tags: list[str] = field(default_factory=list)
    event_candidate_payload: dict[str, Any] = field(default_factory=dict)
