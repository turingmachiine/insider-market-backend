from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from src.backend.rating_service.core.money import quantize_coin
from src.backend.rating_service.core.utils.datetime_utils import utc_now


class RatingEventType(StrEnum):
    PREDICTION_SETTLED = "prediction_settled"
    MARKET_CREATED = "market_created"
    ANALYSIS_PUBLISHED = "analysis_published"
    DAILY_ACTIVE = "daily_active"
    COMMENT_POSTED = "comment_posted"


@dataclass
class RatingEvent:
    id: UUID
    user_id: UUID
    event_type: RatingEventType
    points: int = 0
    is_successful: bool | None = None
    stake: Decimal = Decimal("0")
    payout: Decimal = Decimal("0")
    metadata: dict | None = None
    idempotency_key: str | None = None
    occurred_at: datetime = field(default_factory=utc_now)
    processed_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.stake = quantize_coin(self.stake)
        self.payout = quantize_coin(self.payout)
        if self.stake < 0:
            raise ValueError("Stake must not be negative")
        if self.payout < 0:
            raise ValueError("Payout must not be negative")
        if self.idempotency_key is not None:
            self.idempotency_key = self.idempotency_key.strip() or None

    @property
    def roi_delta(self) -> Decimal:
        if self.stake == 0:
            return Decimal("0")
        return (self.payout - self.stake) / self.stake

    def mark_processed(self) -> None:
        self.processed_at = utc_now()
