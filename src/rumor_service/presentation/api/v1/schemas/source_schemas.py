from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.rumor_service.domain.entities import SourceType


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source_type: SourceType
    handle: str | None = Field(default=None, max_length=255)
    url: str | None = Field(default=None, max_length=500)
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    is_active: bool = True


class SourceResponse(BaseModel):
    id: UUID
    name: str
    source_type: SourceType
    handle: str | None
    url: str | None
    weight: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SourceListResponse(BaseModel):
    items: list[SourceResponse]
    total: int
    limit: int
    offset: int
