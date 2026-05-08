from sqlalchemy import Column, DateTime, Index, Integer, Numeric, String, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.rating_service.core.utils.datetime_utils import utc_now
from src.backend.rating_service.domain.entities import RewardTransactionStatus
from src.backend.rating_service.infrastructure.db.metadata import mapper_registry

reward_transactions_table = Table(
    "rating_reward_transactions",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column("achievement_code", String(100), nullable=False),
    Column("amount", Numeric(20, 6), nullable=False),
    Column(
        "status",
        ENUM(
            RewardTransactionStatus,
            name="rating_reward_transaction_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=False,
        ),
        nullable=False,
    ),
    Column("idempotency_key", String(200), nullable=True),
    Column("attempts", Integer(), nullable=False),
    Column("last_error", String(1000), nullable=True),
    Column("sent_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_rating_reward_transactions_status", "status"),
    Index(
        "ix_rating_reward_transactions_idempotency_key",
        "idempotency_key",
        unique=True,
    ),
)

__all__ = ["reward_transactions_table"]
