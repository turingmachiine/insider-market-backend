from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.backend.notification_service.domain.entities import NotificationTopic


class NotificationPublishRequest(BaseModel):
    topic: NotificationTopic
    event_type: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)
    user_id: UUID | None = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("event_type must not be blank")
        return normalized


class NotificationPublishResponse(BaseModel):
    id: UUID
    topic: NotificationTopic
    event_type: str
    payload: dict[str, Any]
    user_id: UUID | None
    created_at: datetime
    channels: set[str]
