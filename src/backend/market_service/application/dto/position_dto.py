from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.backend.market_service.domain.entities import MarketSide


@dataclass(frozen=True)
class PositionDTO:
    id: UUID
    market_id: UUID
    user_id: UUID
    side: MarketSide
    shares: Decimal
    invested_amount: Decimal
    realized_payout: Decimal
    created_at: datetime
    updated_at: datetime
