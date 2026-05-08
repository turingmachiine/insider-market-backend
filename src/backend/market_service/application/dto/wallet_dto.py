from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class WalletDTO:
    id: UUID
    user_id: UUID
    balance: Decimal
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateWalletDTO:
    user_id: UUID
    initial_balance: Decimal = Decimal("1000")
