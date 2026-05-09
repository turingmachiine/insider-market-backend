from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.market_service.core.money import quantize_coin
from src.market_service.core.utils.datetime_utils import utc_now
from src.market_service.domain.entities.market import MarketSide


@dataclass
class Position:
    id: UUID
    market_id: UUID
    user_id: UUID
    side: MarketSide
    shares: Decimal = Decimal("0")
    invested_amount: Decimal = Decimal("0")
    realized_payout: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.shares = quantize_coin(self.shares)
        self.invested_amount = quantize_coin(self.invested_amount)
        self.realized_payout = quantize_coin(self.realized_payout)

    def add_trade(self, amount: Decimal, shares: Decimal) -> None:
        amount = quantize_coin(amount)
        shares = quantize_coin(shares)
        self.invested_amount = quantize_coin(self.invested_amount + amount)
        self.shares = quantize_coin(self.shares + shares)
        self.updated_at = utc_now()

    def settle(self, payout: Decimal) -> None:
        self.realized_payout = quantize_coin(payout)
        self.updated_at = utc_now()
