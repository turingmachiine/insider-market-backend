from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from src.backend.notification_service.core.utils import utc_now


class NotificationTopic(StrEnum):
    MARKET = "market"
    EVENT = "event"
    RATING = "rating"
    PROFILE = "profile"
    SYSTEM = "system"


@dataclass(frozen=True)
class NotificationEvent:
    topic: NotificationTopic
    event_type: str
    payload: dict[str, Any]
    user_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
