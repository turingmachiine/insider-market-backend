from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.profile_service.domain.entities import ActivityType


@dataclass(frozen=True)
class ActivityDTO:
    id: UUID
    user_id: UUID
    activity_type: ActivityType
    title: str
    description: str | None
    payload: dict | None
    created_at: datetime


@dataclass(frozen=True)
class CreateActivityDTO:
    activity_type: ActivityType
    title: str
    description: str | None = None
    payload: dict | None = None
