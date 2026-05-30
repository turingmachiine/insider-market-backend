from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.profile_service.domain.entities import ActivityType, BalanceTransactionType


class ProfileCreate(BaseModel):
    user_id: UUID
    display_name: str = Field(min_length=1, max_length=120)
    bio: str | None = None
    avatar_url: str | None = Field(default=None, max_length=1000)
    favorite_club: str | None = Field(default=None, max_length=200)
    is_public: bool = False
    initial_balance: Decimal = Field(default=Decimal("1000"), ge=0)


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    bio: str | None = None
    avatar_url: str | None = Field(default=None, max_length=1000)
    favorite_club: str | None = Field(default=None, max_length=200)
    is_public: bool | None = None


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    display_name: str
    bio: str | None
    avatar_url: str | None
    favorite_club: str | None
    is_public: bool
    balance: Decimal
    reserved_balance: Decimal
    available_balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime

    @field_serializer(
        "balance", "reserved_balance", "available_balance", when_used="json"
    )
    @staticmethod
    def serialize_decimal(value: Decimal) -> float:
        return float(value)


class ProfileListResponse(BaseModel):
    items: list[ProfileResponse]
    total: int
    limit: int
    offset: int


class PublicProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    display_name: str
    bio: str | None
    avatar_url: str | None
    favorite_club: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime


class BalanceResponse(BaseModel):
    id: UUID
    user_id: UUID
    balance: Decimal
    reserved_balance: Decimal
    available_balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime

    @field_serializer(
        "balance", "reserved_balance", "available_balance", when_used="json"
    )
    @staticmethod
    def serialize_decimal(value: Decimal) -> float:
        return float(value)


class BalanceOperation(BaseModel):
    transaction_type: BalanceTransactionType
    amount: Decimal = Field(gt=0)
    source: str = Field(min_length=1, max_length=200)
    idempotency_key: str | None = Field(default=None, max_length=200)
    metadata: dict | None = None


class BalanceTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    transaction_type: BalanceTransactionType
    amount: Decimal
    balance_after: Decimal
    reserved_after: Decimal
    source: str
    idempotency_key: str | None
    metadata: dict | None
    created_at: datetime

    @field_serializer("amount", "balance_after", "reserved_after", when_used="json")
    @staticmethod
    def serialize_decimal(value: Decimal) -> float:
        return float(value)


class BalanceTransactionListResponse(BaseModel):
    items: list[BalanceTransactionResponse]


class ActivityCreate(BaseModel):
    activity_type: ActivityType
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    payload: dict | None = None


class ActivityResponse(BaseModel):
    id: UUID
    user_id: UUID
    activity_type: ActivityType
    title: str
    description: str | None
    payload: dict | None
    created_at: datetime


class ActivityListResponse(BaseModel):
    items: list[ActivityResponse]


class AchievementCreate(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    icon_url: str | None = Field(default=None, max_length=1000)


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str
    icon_url: str | None
    created_at: datetime


class AwardAchievement(BaseModel):
    achievement_code: str = Field(min_length=1, max_length=100)
    progress: int = Field(default=100, ge=0)


class UserAchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    achievement_code: str
    progress: int
    awarded_at: datetime
    achievement: AchievementResponse | None


class UserAchievementListResponse(BaseModel):
    items: list[UserAchievementResponse]
