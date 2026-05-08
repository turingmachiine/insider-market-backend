from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Index, Numeric, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.market_service.core.utils.datetime_utils import utc_now
from src.backend.market_service.domain.entities import MarketSide
from src.backend.market_service.infrastructure.db.metadata import mapper_registry

bets_table = Table(
    "bets",
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
    Column("amount", Numeric(20, 6), nullable=False),
    Column("shares", Numeric(20, 6), nullable=False),
    Column("probability_before", Float, nullable=False),
    Column("probability_after", Float, nullable=False),
    Column("odds_before", Float, nullable=False),
    Column("odds_after", Float, nullable=False),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Index("ix_bets_market_id", "market_id"),
    Index("ix_bets_user_id", "user_id"),
    Index("ix_bets_created_at", "created_at"),
)

__all__ = ["bets_table"]
