from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from src.backend.market_service.domain.entities import (
    MarketOutcome,
    MarketSide,
    MarketStatus,
)


class MarketCreate(BaseModel):
    event_id: UUID
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    initial_probability: float = Field(ge=0.01, le=0.99)
    liquidity_parameter: Decimal = Field(gt=0)
    close_at: datetime | None = None
    created_by_user_id: UUID | None = None
    activate: bool = True


class BetCreate(BaseModel):
    user_id: UUID
    side: MarketSide
    amount: Decimal = Field(gt=0)


class MarketResolve(BaseModel):
    outcome: MarketOutcome
    resolved_by_user_id: UUID | None = None


class MarketResponse(BaseModel):
    id: UUID
    event_id: UUID
    title: str
    description: str
    initial_probability: float
    liquidity_parameter: Decimal
    yes_pool: Decimal
    no_pool: Decimal
    yes_probability: float
    no_probability: float
    yes_odds: float
    no_odds: float
    status: MarketStatus
    close_at: datetime | None
    outcome: MarketOutcome | None
    created_by_user_id: UUID | None
    resolved_by_user_id: UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("liquidity_parameter", "yes_pool", "no_pool", when_used="json")
    @staticmethod
    def serialize_coin_value(value: Decimal) -> float:
        return float(value)


class BetResponse(BaseModel):
    id: UUID
    market_id: UUID
    user_id: UUID
    side: MarketSide
    amount: Decimal
    shares: Decimal
    probability_before: float
    probability_after: float
    odds_before: float
    odds_after: float
    created_at: datetime

    @field_serializer("amount", "shares", when_used="json")
    @staticmethod
    def serialize_coin_value(value: Decimal) -> float:
        return float(value)


class PositionResponse(BaseModel):
    id: UUID
    market_id: UUID
    user_id: UUID
    side: MarketSide
    shares: Decimal
    invested_amount: Decimal
    realized_payout: Decimal
    created_at: datetime
    updated_at: datetime

    @field_serializer("shares", "invested_amount", "realized_payout", when_used="json")
    @staticmethod
    def serialize_coin_value(value: Decimal) -> float:
        return float(value)


class MarketListResponse(BaseModel):
    items: list[MarketResponse]
    total: int
    limit: int
    offset: int


class BetListResponse(BaseModel):
    items: list[BetResponse]
    total: int
    limit: int
    offset: int


class PositionListResponse(BaseModel):
    items: list[PositionResponse]
    total: int
