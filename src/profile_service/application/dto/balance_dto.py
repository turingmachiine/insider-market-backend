from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.profile_service.domain.entities import BalanceTransactionType


@dataclass(frozen=True)
class UserBalanceDTO:
    id: UUID
    user_id: UUID
    balance: Decimal
    reserved_balance: Decimal
    available_balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class BalanceTransactionDTO:
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


@dataclass(frozen=True)
class BalanceOperationDTO:
    transaction_type: BalanceTransactionType
    amount: Decimal
    source: str
    idempotency_key: str | None = None
    metadata: dict | None = None
