from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RawPublicationCreate(BaseModel):
    source_id: UUID
    text: str = Field(min_length=1)
    external_id: str | None = Field(default=None, max_length=255)
    url: str | None = Field(default=None, max_length=500)
    published_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class RawPublicationResponse(BaseModel):
    id: UUID
    source_id: UUID
    text: str
    external_id: str | None
    url: str | None
    published_at: datetime | None
    collected_at: datetime
    payload: dict[str, Any]


class RawPublicationListResponse(BaseModel):
    items: list[RawPublicationResponse]
    total: int
    limit: int
    offset: int
