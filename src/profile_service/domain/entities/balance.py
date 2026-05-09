from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from src.profile_service.core.money import quantize_coin
from src.profile_service.core.utils.datetime_utils import utc_now


class BalanceTransactionType(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"
    RESERVE = "reserve"
    RELEASE = "release"


@dataclass
class UserBalance:
    id: UUID
    user_id: UUID
    balance: Decimal
    reserved_balance: Decimal = Decimal("0")
    currency: str = "COIN"
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.balance = quantize_coin(self.balance)
        self.reserved_balance = quantize_coin(self.reserved_balance)
        if self.balance < 0:
            raise ValueError("Balance must not be negative")
        if self.reserved_balance < 0:
            raise ValueError("Reserved balance must not be negative")

    @property
    def available_balance(self) -> Decimal:
        return quantize_coin(self.balance - self.reserved_balance)

    def credit(self, amount: Decimal) -> None:
        amount = self._positive_amount(amount)
        self.balance = quantize_coin(self.balance + amount)
        self.updated_at = utc_now()

    def debit(self, amount: Decimal) -> None:
        amount = self._positive_amount(amount)
        if self.available_balance < amount:
            raise ValueError("Insufficient available balance")
        self.balance = quantize_coin(self.balance - amount)
        self.updated_at = utc_now()

    def reserve(self, amount: Decimal) -> None:
        amount = self._positive_amount(amount)
        if self.available_balance < amount:
            raise ValueError("Insufficient available balance")
        self.reserved_balance = quantize_coin(self.reserved_balance + amount)
        self.updated_at = utc_now()

    def release(self, amount: Decimal) -> None:
        amount = self._positive_amount(amount)
        if self.reserved_balance < amount:
            raise ValueError("Insufficient reserved balance")
        self.reserved_balance = quantize_coin(self.reserved_balance - amount)
        self.updated_at = utc_now()

    @staticmethod
    def _positive_amount(amount: Decimal) -> Decimal:
        amount = quantize_coin(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount


@dataclass
class BalanceTransaction:
    id: UUID
    user_id: UUID
    transaction_type: BalanceTransactionType
    amount: Decimal
    balance_after: Decimal
    reserved_after: Decimal
    source: str
    idempotency_key: str | None = None
    metadata: dict | None = None
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.amount = quantize_coin(self.amount)
        self.balance_after = quantize_coin(self.balance_after)
        self.reserved_after = quantize_coin(self.reserved_after)
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        if not self.source.strip():
            raise ValueError("Transaction source must not be empty")
