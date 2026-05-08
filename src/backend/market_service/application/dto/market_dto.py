from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.backend.market_service.domain.entities import (
    MarketOutcome,
    MarketSide,
    MarketStatus,
)


@dataclass(frozen=True)
class MarketDTO:
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


@dataclass(frozen=True)
class CreateMarketDTO:
    event_id: UUID
    title: str
    description: str
    initial_probability: float
    liquidity_parameter: Decimal
    close_at: datetime | None = None
    created_by_user_id: UUID | None = None
    activate: bool = True


@dataclass(frozen=True)
class PlaceBetDTO:
    user_id: UUID
    side: MarketSide
    amount: Decimal


@dataclass(frozen=True)
class ResolveMarketDTO:
    outcome: MarketOutcome
    resolved_by_user_id: UUID | None = None
