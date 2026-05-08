from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.backend.rating_service.domain.entities import (
    AchievementRarity,
    RatingEventType,
    RewardTransactionStatus,
    UserStatus,
)


@dataclass(frozen=True)
class RatingProfileDTO:
    user_id: UUID
    rating: int
    xp: int
    level: int
    status: UserStatus
    total_predictions: int
    correct_predictions: int
    accuracy: float
    current_streak: int
    best_streak: int
    markets_created: int
    analyses_published: int
    comments_posted: int
    active_days: int
    roi_percent: float
    last_event_at: datetime | None
    updated_at: datetime


@dataclass(frozen=True)
class CreateRatingEventDTO:
    user_id: UUID
    event_type: RatingEventType
    points: int = 0
    is_successful: bool | None = None
    stake: Decimal = Decimal("0")
    payout: Decimal = Decimal("0")
    metadata: dict | None = None
    idempotency_key: str | None = None
    occurred_at: datetime | None = None


@dataclass(frozen=True)
class RatingEventDTO:
    id: UUID
    user_id: UUID
    event_type: RatingEventType
    points: int
    is_successful: bool | None
    stake: Decimal
    payout: Decimal
    metadata: dict | None
    idempotency_key: str | None
    occurred_at: datetime
    processed_at: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class AchievementDefinitionDTO:
    code: str
    name: str
    description: str
    metric: str
    threshold: int
    reward_amount: Decimal
    rarity: AchievementRarity
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class CreateAchievementDefinitionDTO:
    code: str
    name: str
    description: str
    metric: str
    threshold: int
    reward_amount: Decimal
    rarity: AchievementRarity = AchievementRarity.COMMON
    is_active: bool = True


@dataclass(frozen=True)
class UserAchievementDTO:
    id: UUID
    user_id: UUID
    achievement_code: str
    reward_amount: Decimal
    awarded_at: datetime
    achievement: AchievementDefinitionDTO | None = None


@dataclass(frozen=True)
class RewardTransactionDTO:
    id: UUID
    user_id: UUID
    achievement_code: str
    amount: Decimal
    status: RewardTransactionStatus
    idempotency_key: str | None
    attempts: int
    last_error: str | None
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class RatingRecalculationDTO:
    events_processed: int
    achievements_awarded: int
    rewards_dispatched: int
