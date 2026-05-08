from sqlalchemy import Boolean, Column, DateTime, Index, Integer, Numeric, String, Table
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.rating_service.core.utils.datetime_utils import utc_now
from src.backend.rating_service.domain.entities import RatingEventType
from src.backend.rating_service.infrastructure.db.metadata import mapper_registry

rating_events_table = Table(
    "rating_events",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column(
        "event_type",
        ENUM(
            RatingEventType,
            name="rating_event_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=False,
        ),
        nullable=False,
    ),
    Column("points", Integer(), nullable=False),
    Column("is_successful", Boolean(), nullable=True),
    Column("stake", Numeric(20, 6), nullable=False),
    Column("payout", Numeric(20, 6), nullable=False),
    Column("metadata", JSONB(), nullable=True),
    Column("idempotency_key", String(200), nullable=True),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("processed_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Index("ix_rating_events_user_id", "user_id"),
    Index("ix_rating_events_processed_at", "processed_at"),
    Index("ix_rating_events_idempotency_key", "idempotency_key", unique=True),
)

__all__ = ["rating_events_table"]
