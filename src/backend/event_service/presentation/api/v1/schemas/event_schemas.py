from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.backend.event_service.domain.entities import EventOutcome, EventStatus


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    source_rumor_id: UUID | None = None
    candidate_payload: dict[str, Any] = Field(default_factory=dict)
    deadline_at: datetime | None = None
    resolution_rules: str | None = None
    created_by_user_id: UUID | None = None
    submit_for_moderation: bool = False


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, min_length=1)
    deadline_at: datetime | None = None
    resolution_rules: str | None = None
    candidate_payload: dict[str, Any] | None = None


class EventReject(BaseModel):
    notes: str | None = None


class EventResolve(BaseModel):
    outcome: EventOutcome
    resolved_by_user_id: UUID | None = None
    notes: str | None = None


class EventCancel(BaseModel):
    notes: str | None = None


class EventResponse(BaseModel):
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


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int
    limit: int
    offset: int
