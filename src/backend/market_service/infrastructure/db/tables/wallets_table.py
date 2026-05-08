from sqlalchemy import Column, DateTime, Index, Numeric, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.market_service.core.utils.datetime_utils import utc_now
from src.backend.market_service.infrastructure.db.metadata import mapper_registry

wallets_table = Table(
    "wallets",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False, unique=True),
    Column("balance", Numeric(20, 6), nullable=False),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_wallets_user_id", "user_id", unique=True),
)

__all__ = ["wallets_table"]
