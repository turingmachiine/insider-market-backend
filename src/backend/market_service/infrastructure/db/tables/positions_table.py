from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, Numeric, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.market_service.core.utils.datetime_utils import utc_now
from src.backend.market_service.domain.entities import MarketSide
from src.backend.market_service.infrastructure.db.metadata import mapper_registry

positions_table = Table(
    "positions",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column(
        "market_id",
        PG_UUID(as_uuid=True),
        ForeignKey("markets.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column(
        "side",
        SAEnum(
            MarketSide,
            name="market_side",
            values_callable=lambda enum: [value.value for value in enum],
            create_type=False,
        ),
        nullable=False,
    ),
    Column("shares", Numeric(20, 6), nullable=False, default=0),
    Column("invested_amount", Numeric(20, 6), nullable=False, default=0),
    Column("realized_payout", Numeric(20, 6), nullable=False, default=0),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    UniqueConstraint(
        "market_id", "user_id", "side", name="uq_positions_market_user_side"
    ),
    Index("ix_positions_market_id", "market_id"),
    Index("ix_positions_user_id", "user_id"),
)

__all__ = ["positions_table"]
