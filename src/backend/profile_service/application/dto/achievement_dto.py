from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AchievementDTO:
    code: str
    name: str
    description: str
    icon_url: str | None
    created_at: datetime


@dataclass(frozen=True)
class UserAchievementDTO:
    id: UUID
    user_id: UUID
    achievement_code: str
    progress: int
    awarded_at: datetime
    achievement: AchievementDTO | None = None


@dataclass(frozen=True)
class CreateAchievementDTO:
    code: str
    name: str
    description: str
    icon_url: str | None = None


@dataclass(frozen=True)
class AwardAchievementDTO:
    achievement_code: str
    progress: int = 100
