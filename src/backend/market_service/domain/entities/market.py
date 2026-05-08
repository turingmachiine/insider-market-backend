from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from src.backend.market_service.core.money import quantize_coin
from src.backend.market_service.core.utils.datetime_utils import utc_now


class MarketStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class MarketOutcome(StrEnum):
    YES = "yes"
    NO = "no"
    VOID = "void"


class MarketSide(StrEnum):
    YES = "yes"
    NO = "no"


@dataclass
class Market:
    id: UUID
    event_id: UUID
    title: str
    description: str
    initial_probability: float
    liquidity_parameter: Decimal
    yes_pool: Decimal
    no_pool: Decimal
    status: MarketStatus = MarketStatus.DRAFT
    close_at: datetime | None = None
    outcome: MarketOutcome | None = None
    created_by_user_id: UUID | None = None
    resolved_by_user_id: UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.liquidity_parameter = quantize_coin(self.liquidity_parameter)
        self.yes_pool = quantize_coin(self.yes_pool)
        self.no_pool = quantize_coin(self.no_pool)

    @property
    def yes_probability(self) -> float:
        return float(self.no_pool / (self.yes_pool + self.no_pool))

    @property
    def no_probability(self) -> float:
        return float(self.yes_pool / (self.yes_pool + self.no_pool))

    @property
    def yes_odds(self) -> float:
        return 1 / self.yes_probability

    @property
    def no_odds(self) -> float:
        return 1 / self.no_probability

    def activate(self) -> None:
        if self.status != MarketStatus.DRAFT:
            raise ValueError(f"Cannot activate market in {self.status} status")
        self.status = MarketStatus.ACTIVE
        self._touch()

    def pause(self) -> None:
        if self.status != MarketStatus.ACTIVE:
            raise ValueError(f"Cannot pause market in {self.status} status")
        self.status = MarketStatus.PAUSED
        self._touch()

    def resume(self) -> None:
        if self.status != MarketStatus.PAUSED:
            raise ValueError(f"Cannot resume market in {self.status} status")
        self.status = MarketStatus.ACTIVE
        self._touch()

    def close(self) -> None:
        if self.status not in {MarketStatus.ACTIVE, MarketStatus.PAUSED}:
            raise ValueError(f"Cannot close market in {self.status} status")
        self.status = MarketStatus.CLOSED
        self._touch()

    def resolve(
        self,
        outcome: MarketOutcome,
        resolved_by_user_id: UUID | None = None,
    ) -> None:
        if self.status not in {
            MarketStatus.ACTIVE,
            MarketStatus.PAUSED,
            MarketStatus.CLOSED,
        }:
            raise ValueError(f"Cannot resolve market in {self.status} status")
        self.status = MarketStatus.RESOLVED
        self.outcome = outcome
        self.resolved_by_user_id = resolved_by_user_id
        self.resolved_at = utc_now()
        self._touch()

    def cancel(self) -> None:
        if self.status in {MarketStatus.RESOLVED, MarketStatus.CANCELLED}:
            raise ValueError(f"Cannot cancel market in {self.status} status")
        self.status = MarketStatus.CANCELLED
        self.outcome = MarketOutcome.VOID
        self._touch()

    def update_pools(self, yes_pool: Decimal, no_pool: Decimal) -> None:
        """Обновляет AMM-пулы после сделки и фиксирует время изменения рынка."""
        self.yes_pool = quantize_coin(yes_pool)
        self.no_pool = quantize_coin(no_pool)
        self._touch()

    def _touch(self) -> None:
        self.updated_at = utc_now()
