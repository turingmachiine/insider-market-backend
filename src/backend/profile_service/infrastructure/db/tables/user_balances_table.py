from sqlalchemy import Column, DateTime, Index, Numeric, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.profile_service.core.utils.datetime_utils import utc_now
from src.backend.profile_service.infrastructure.db.metadata import mapper_registry

user_balances_table = Table(
    "user_balances",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False, unique=True),
    Column("balance", Numeric(20, 6), nullable=False),
    Column("reserved_balance", Numeric(20, 6), nullable=False),
    Column("currency", String(16), nullable=False),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_user_balances_user_id", "user_id", unique=True),
)

__all__ = ["user_balances_table"]
