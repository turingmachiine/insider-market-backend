from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class WalletCreate(BaseModel):
    user_id: UUID
    initial_balance: Decimal = Field(default=Decimal("1000"), ge=0)


class WalletResponse(BaseModel):
    id: UUID
    user_id: UUID
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    @field_serializer("balance", when_used="json")
    @staticmethod
    def serialize_balance(value: Decimal) -> float:
        return float(value)
