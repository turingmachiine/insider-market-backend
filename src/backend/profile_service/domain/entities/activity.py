from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.backend.profile_service.core.utils.datetime_utils import utc_now


class ActivityType(StrEnum):
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    BALANCE_CHANGED = "balance_changed"
    ACHIEVEMENT_AWARDED = "achievement_awarded"
    MARKET_BET_PLACED = "market_bet_placed"
    MARKET_RESOLVED = "market_resolved"


@dataclass
class Activity:
    id: UUID
    user_id: UUID
    activity_type: ActivityType
    title: str
    description: str | None = None
    payload: dict | None = None
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Activity title must not be empty")
