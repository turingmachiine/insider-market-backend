from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, Index, Numeric, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.market_service.core.utils.datetime_utils import utc_now
from src.market_service.domain.entities import MarketOutcome, MarketStatus
from src.market_service.infrastructure.db.metadata import mapper_registry

markets_table = Table(
    "markets",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("event_id", PG_UUID(as_uuid=True), nullable=False, unique=True),
    Column("title", String(500), nullable=False),
    Column("description", Text, nullable=False),
    Column("initial_probability", Float, nullable=False),
    Column("liquidity_parameter", Numeric(20, 6), nullable=False),
    Column("yes_pool", Numeric(20, 6), nullable=False),
    Column("no_pool", Numeric(20, 6), nullable=False),
    Column(
        "status",
        SAEnum(
            MarketStatus,
            name="market_status",
            values_callable=lambda enum: [value.value for value in enum],
            create_type=False,
        ),
        nullable=False,
        default=MarketStatus.DRAFT,
    ),
    Column("close_at", DateTime(timezone=True), nullable=True),
    Column(
        "outcome",
        SAEnum(
            MarketOutcome,
            name="market_outcome",
            values_callable=lambda enum: [value.value for value in enum],
            create_type=False,
        ),
        nullable=True,
    ),
    Column("created_by_user_id", PG_UUID(as_uuid=True), nullable=True),
    Column("resolved_by_user_id", PG_UUID(as_uuid=True), nullable=True),
    Column("resolved_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_markets_event_id", "event_id", unique=True),
    Index("ix_markets_status", "status"),
    Index("ix_markets_close_at", "close_at"),
)

__all__ = ["markets_table"]
