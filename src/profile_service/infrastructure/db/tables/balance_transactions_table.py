from sqlalchemy import Column, DateTime, Index, Numeric, String, Table
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.profile_service.core.utils.datetime_utils import utc_now
from src.profile_service.domain.entities import BalanceTransactionType
from src.profile_service.infrastructure.db.metadata import mapper_registry

balance_transaction_type_enum = ENUM(
    BalanceTransactionType,
    name="profile_balance_transaction_type",
    values_callable=lambda enum_cls: [item.value for item in enum_cls],
    create_type=False,
)

balance_transactions_table = Table(
    "balance_transactions",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column("transaction_type", balance_transaction_type_enum, nullable=False),
    Column("amount", Numeric(20, 6), nullable=False),
    Column("balance_after", Numeric(20, 6), nullable=False),
    Column("reserved_after", Numeric(20, 6), nullable=False),
    Column("source", String(200), nullable=False),
    Column("idempotency_key", String(200), nullable=True, unique=True),
    Column("metadata", JSONB, nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Index("ix_balance_transactions_user_id", "user_id"),
    Index("ix_balance_transactions_created_at", "created_at"),
    Index(
        "ix_balance_transactions_idempotency_key",
        "idempotency_key",
        unique=True,
    ),
)

__all__ = ["balance_transactions_table", "balance_transaction_type_enum"]
