from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from src.notification_service.domain.entities import NotificationTopic


@dataclass(frozen=True)
class SubscriptionDTO:
    topics: set[NotificationTopic]
    user_id: UUID | None = None


@dataclass(frozen=True)
class PublishNotificationDTO:
    topic: NotificationTopic
    event_type: str
    payload: dict[str, Any]
    user_id: UUID | None = None


@dataclass(frozen=True)
class NotificationEventDTO:
    id: UUID
    topic: NotificationTopic
    event_type: str
    payload: dict[str, Any]
    user_id: UUID | None
    created_at: datetime
    channels: set[str] = field(default_factory=set)
