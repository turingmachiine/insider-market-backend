from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from src.rating_service.core.money import quantize_coin
from src.rating_service.core.utils.datetime_utils import utc_now


class AchievementRarity(StrEnum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class AchievementDefinition:
    code: str
    name: str
    description: str
    metric: str
    threshold: int
    reward_amount: Decimal
    rarity: AchievementRarity = AchievementRarity.COMMON
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.code = self.code.strip().lower()
        self.name = self.name.strip()
        self.description = self.description.strip()
        self.metric = self.metric.strip()
        self.reward_amount = quantize_coin(self.reward_amount)
        if not self.code:
            raise ValueError("Achievement code must not be empty")
        if not self.name:
            raise ValueError("Achievement name must not be empty")
        if self.threshold <= 0:
            raise ValueError("Achievement threshold must be positive")
        if self.reward_amount < 0:
            raise ValueError("Achievement reward must not be negative")


@dataclass
class UserAchievement:
    id: UUID
    user_id: UUID
    achievement_code: str
    reward_amount: Decimal
    awarded_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.achievement_code = self.achievement_code.strip().lower()
        self.reward_amount = quantize_coin(self.reward_amount)
        if not self.achievement_code:
            raise ValueError("Achievement code must not be empty")
