from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.backend.rating_service.domain.entities import (
    AchievementRarity,
    RatingEventType,
    RewardTransactionStatus,
    UserStatus,
)


class RatingEventCreate(BaseModel):
    user_id: UUID
    event_type: RatingEventType
    points: int = Field(default=0, ge=0)
    is_successful: bool | None = None
    stake: Decimal = Field(default=Decimal("0"), ge=0)
    payout: Decimal = Field(default=Decimal("0"), ge=0)
    metadata: dict | None = None
    idempotency_key: str | None = Field(default=None, max_length=200)
    occurred_at: datetime | None = None


class RatingEventResponse(BaseModel):
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

    @field_serializer("stake", "payout", when_used="json")
    @staticmethod
    def serialize_decimal(value: Decimal) -> float:
        return float(value)


class RatingProfileResponse(BaseModel):
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


class RatingProfileListResponse(BaseModel):
    items: list[RatingProfileResponse]
    total: int
    limit: int
    offset: int


class AchievementDefinitionCreate(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    metric: str = Field(min_length=1, max_length=100)
    threshold: int = Field(gt=0)
    reward_amount: Decimal = Field(ge=0)
    rarity: AchievementRarity = AchievementRarity.COMMON
    is_active: bool = True


class AchievementDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str
    metric: str
    threshold: int
    reward_amount: Decimal
    rarity: AchievementRarity
    is_active: bool
    created_at: datetime

    @field_serializer("reward_amount", when_used="json")
    @staticmethod
    def serialize_decimal(value: Decimal) -> float:
        return float(value)


class AchievementDefinitionListResponse(BaseModel):
    items: list[AchievementDefinitionResponse]


class UserAchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    achievement_code: str
    reward_amount: Decimal
    awarded_at: datetime
    achievement: AchievementDefinitionResponse | None

    @field_serializer("reward_amount", when_used="json")
    @staticmethod
    def serialize_decimal(value: Decimal) -> float:
        return float(value)


class UserAchievementListResponse(BaseModel):
    items: list[UserAchievementResponse]


class RewardTransactionResponse(BaseModel):
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

    @field_serializer("amount", when_used="json")
    @staticmethod
    def serialize_decimal(value: Decimal) -> float:
        return float(value)


class RewardTransactionListResponse(BaseModel):
    items: list[RewardTransactionResponse]


class RatingRecalculationResponse(BaseModel):
    events_processed: int
    achievements_awarded: int
    rewards_dispatched: int
