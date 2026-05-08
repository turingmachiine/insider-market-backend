from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.backend.market_service.domain.entities import MarketSide


@dataclass(frozen=True)
class BetDTO:
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
