from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.rumor_service.domain.entities import RumorStatus


class RumorCreate(BaseModel):
    source_id: UUID
    title: str = Field(min_length=1, max_length=500)
    text: str = Field(min_length=1)
    normalized_text: str | None = None
    raw_publication_id: UUID | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    status: RumorStatus = RumorStatus.NEW
    tags: list[str] = Field(default_factory=list)
    event_candidate_payload: dict[str, Any] = Field(default_factory=dict)


class RumorStatusUpdate(BaseModel):
    status: RumorStatus


class RumorResponse(BaseModel):
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


class RumorListResponse(BaseModel):
    items: list[RumorResponse]
    total: int
    limit: int
    offset: int
