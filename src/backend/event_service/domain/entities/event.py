from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from src.backend.event_service.core.utils.datetime_utils import utc_now


class EventStatus(StrEnum):
    DRAFT = "draft"
    PENDING_MODERATION = "pending_moderation"
    ACTIVE = "active"
    REJECTED = "rejected"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class EventOutcome(StrEnum):
    YES = "yes"
    NO = "no"
    VOID = "void"


TERMINAL_STATUSES = {
    EventStatus.REJECTED,
    EventStatus.RESOLVED,
    EventStatus.CANCELLED,
}


@dataclass
class Event:
    id: UUID
    title: str
    description: str
    status: EventStatus = EventStatus.DRAFT
    source_rumor_id: UUID | None = None
    candidate_payload: dict[str, Any] = field(default_factory=dict)
    deadline_at: datetime | None = None
    resolution_rules: str | None = None
    outcome: EventOutcome | None = None
    resolution_notes: str | None = None
    created_by_user_id: UUID | None = None
    resolved_by_user_id: UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def submit_for_moderation(self) -> None:
        self._ensure_status(EventStatus.DRAFT)
        self.status = EventStatus.PENDING_MODERATION
        self._touch()

    def approve(self) -> None:
        self._ensure_status(EventStatus.PENDING_MODERATION)
        self.status = EventStatus.ACTIVE
        self._touch()

    def reject(self, notes: str | None = None) -> None:
        self._ensure_status(EventStatus.PENDING_MODERATION)
        self.status = EventStatus.REJECTED
        self.resolution_notes = notes
        self._touch()

    def resolve(
        self,
        outcome: EventOutcome,
        resolved_by_user_id: UUID | None = None,
        notes: str | None = None,
    ) -> None:
        self._ensure_status(EventStatus.ACTIVE)
        self.status = EventStatus.RESOLVED
        self.outcome = outcome
        self.resolved_by_user_id = resolved_by_user_id
        self.resolution_notes = notes
        self.resolved_at = utc_now()
        self._touch()

    def cancel(self, notes: str | None = None) -> None:
        if self.status in TERMINAL_STATUSES:
            raise ValueError(f"Cannot cancel event in {self.status} status")
        self.status = EventStatus.CANCELLED
        self.resolution_notes = notes
        self._touch()

    def update_details(
        self,
        title: str | None = None,
        description: str | None = None,
        deadline_at: datetime | None = None,
        resolution_rules: str | None = None,
        candidate_payload: dict[str, Any] | None = None,
    ) -> None:
        if self.status in TERMINAL_STATUSES:
            raise ValueError(f"Cannot edit event in {self.status} status")
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if deadline_at is not None:
            self.deadline_at = deadline_at
        if resolution_rules is not None:
            self.resolution_rules = resolution_rules
        if candidate_payload is not None:
            self.candidate_payload = candidate_payload
        self._touch()

    def _ensure_status(self, expected: EventStatus) -> None:
        if self.status != expected:
            raise ValueError(f"Expected event status {expected}, got {self.status}")

    def _touch(self) -> None:
        self.updated_at = utc_now()
