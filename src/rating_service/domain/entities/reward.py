from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from src.rating_service.core.money import quantize_coin
from src.rating_service.core.utils.datetime_utils import utc_now


class RewardTransactionStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class RewardTransaction:
    id: UUID
    user_id: UUID
    achievement_code: str
    amount: Decimal
    status: RewardTransactionStatus = RewardTransactionStatus.PENDING
    idempotency_key: str | None = None
    attempts: int = 0
    last_error: str | None = None
    sent_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.achievement_code = self.achievement_code.strip().lower()
        self.amount = quantize_coin(self.amount)
        if self.amount < 0:
            raise ValueError("Reward amount must not be negative")
        if self.idempotency_key is None:
            self.idempotency_key = (
                f"rating.achievement.{self.user_id}.{self.achievement_code}"
            )

    def mark_sent(self) -> None:
        self.status = RewardTransactionStatus.SENT
        self.sent_at = utc_now()
        self.updated_at = utc_now()

    def mark_failed(self, error: str) -> None:
        self.status = RewardTransactionStatus.FAILED
        self.attempts += 1
        self.last_error = error[:1000]
        self.updated_at = utc_now()
