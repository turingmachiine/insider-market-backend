from sqlalchemy import Column, DateTime, Enum, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.market_service.core.utils.datetime_utils import utc_now
from src.market_service.domain.entities import MarketAuditAction
from src.market_service.infrastructure.db.metadata import mapper_registry

audit_logs_table = Table(
    "audit_logs",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("actor_user_id", PG_UUID(as_uuid=True), nullable=True, index=True),
    Column(
        "action",
        Enum(
            MarketAuditAction,
            name="market_audit_action",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=False,
        ),
        nullable=False,
        index=True,
    ),
    Column("target_type", String(50), nullable=False),
    Column("target_id", String(100), nullable=True),
    Column("before", JSONB(), nullable=True),
    Column("after", JSONB(), nullable=True),
    Column("correlation_id", String(100), nullable=True, index=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
)

__all__ = ["audit_logs_table"]
