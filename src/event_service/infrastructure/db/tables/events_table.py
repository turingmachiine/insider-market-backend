from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Index, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.event_service.core.utils.datetime_utils import utc_now
from src.event_service.domain.entities import EventOutcome, EventStatus
from src.event_service.infrastructure.db.metadata import mapper_registry

events_table = Table(
    "events",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("title", String(500), nullable=False),
    Column("description", Text, nullable=False),
    Column(
        "status",
        SAEnum(
            EventStatus,
            name="event_status",
            values_callable=lambda enum: [value.value for value in enum],
            create_type=False,
        ),
        nullable=False,
        default=EventStatus.DRAFT,
    ),
    Column("source_rumor_id", PG_UUID(as_uuid=True), nullable=True),
    Column("candidate_payload", JSONB, nullable=False, default=dict),
    Column("deadline_at", DateTime(timezone=True), nullable=True),
    Column("resolution_rules", Text, nullable=True),
    Column(
        "outcome",
        SAEnum(
            EventOutcome,
            name="event_outcome",
            values_callable=lambda enum: [value.value for value in enum],
            create_type=False,
        ),
        nullable=True,
    ),
    Column("resolution_notes", Text, nullable=True),
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
    Index("ix_events_status", "status"),
    Index("ix_events_source_rumor", "source_rumor_id"),
    Index("ix_events_deadline", "deadline_at"),
    Index("ix_events_created_at", "created_at"),
)

__all__ = ["events_table"]
