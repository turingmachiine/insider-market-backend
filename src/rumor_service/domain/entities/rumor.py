from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from src.rumor_service.core.utils.datetime_utils import utc_now


class RumorStatus(StrEnum):
    NEW = "new"
    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class Rumor:
    id: UUID
    source_id: UUID
    title: str
    text: str
    normalized_text: str | None = None
    raw_publication_id: UUID | None = None
    confidence_score: float = 0.0
    status: RumorStatus = RumorStatus.NEW
    tags: list[str] = field(default_factory=list)
    event_candidate_payload: dict[str, Any] = field(default_factory=dict)
    event_id: UUID | None = None
    is_public: bool = False
    published_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def update_status(self, status: RumorStatus) -> None:
        self.status = status
        if status == RumorStatus.APPROVED:
            self.publish()
        self.updated_at = utc_now()

    def publish(self) -> None:
        self.is_public = True
        if self.published_at is None:
            self.published_at = utc_now()
