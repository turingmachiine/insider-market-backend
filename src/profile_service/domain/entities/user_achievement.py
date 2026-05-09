from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.profile_service.core.utils.datetime_utils import utc_now


@dataclass
class UserAchievement:
    id: UUID
    user_id: UUID
    achievement_code: str
    progress: int = 100
    awarded_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.achievement_code = self.achievement_code.strip().lower()
        if not self.achievement_code:
            raise ValueError("Achievement code must not be empty")
        if self.progress < 0:
            raise ValueError("Achievement progress must not be negative")
