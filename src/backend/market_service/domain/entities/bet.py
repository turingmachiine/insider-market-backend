from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.backend.market_service.core.money import quantize_coin
from src.backend.market_service.core.utils.datetime_utils import utc_now
from src.backend.market_service.domain.entities.market import MarketSide


@dataclass
class Bet:
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
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.amount = quantize_coin(self.amount)
        self.shares = quantize_coin(self.shares)
