from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.market_service.core.money import quantize_coin
from src.market_service.core.utils.datetime_utils import utc_now


@dataclass
class Wallet:
    id: UUID
    user_id: UUID
    balance: Decimal
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.balance = quantize_coin(self.balance)

    def debit(self, amount: Decimal) -> None:
        amount = quantize_coin(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient wallet balance")
        self.balance = quantize_coin(self.balance - amount)
        self.updated_at = utc_now()

    def credit(self, amount: Decimal) -> None:
        amount = quantize_coin(amount)
        if amount < 0:
            raise ValueError("Amount must not be negative")
        self.balance = quantize_coin(self.balance + amount)
        self.updated_at = utc_now()
