from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from src.event_service.domain.entities import EventOutcome, EventStatus


@dataclass(frozen=True)
class EventDTO:
    id: UUID
    title: str
    description: str
    status: EventStatus
    source_rumor_id: UUID | None
    candidate_payload: dict[str, Any]
    deadline_at: datetime | None
    resolution_rules: str | None
    outcome: EventOutcome | None
    resolution_notes: str | None
    created_by_user_id: UUID | None
    resolved_by_user_id: UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateEventDTO:
    title: str
    description: str
    source_rumor_id: UUID | None = None
    candidate_payload: dict[str, Any] = field(default_factory=dict)
    deadline_at: datetime | None = None
    resolution_rules: str | None = None
    created_by_user_id: UUID | None = None
    submit_for_moderation: bool = False


@dataclass(frozen=True)
class UpdateEventDTO:
    title: str | None = None
    description: str | None = None
    deadline_at: datetime | None = None
    resolution_rules: str | None = None
    candidate_payload: dict[str, Any] | None = None


@dataclass(frozen=True)
class ApproveEventDTO:
    approved_by_user_id: UUID | None = None


@dataclass(frozen=True)
class RejectEventDTO:
    notes: str | None = None


@dataclass(frozen=True)
class ResolveEventDTO:
    outcome: EventOutcome
    resolved_by_user_id: UUID | None = None
    notes: str | None = None


@dataclass(frozen=True)
class CancelEventDTO:
    notes: str | None = None
