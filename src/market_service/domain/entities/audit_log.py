from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.market_service.core.utils.datetime_utils import utc_now


class MarketAuditAction(StrEnum):
    WALLET_CREATE = "wallet_create"
    BET_PLACE = "bet_place"
    MARKET_RESOLVE = "market_resolve"


@dataclass
class AuditLog:
    id: UUID
    action: MarketAuditAction
    target_type: str
    target_id: str | None = None
    actor_user_id: UUID | None = None
    before: dict | None = None
    after: dict | None = None
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
