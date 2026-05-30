from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Index, String, Table, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.rumor_service.core.utils.datetime_utils import utc_now
from src.rumor_service.domain.entities import RumorStatus
from src.rumor_service.infrastructure.db.metadata import mapper_registry

rumors_table = Table(
    "rumors",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column(
        "source_id",
        PG_UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "raw_publication_id",
        PG_UUID(as_uuid=True),
        ForeignKey("raw_publications.id", ondelete="SET NULL"),
        nullable=True,
    ),
    Column("title", String(500), nullable=False),
    Column("text", Text, nullable=False),
    Column("normalized_text", Text, nullable=True),
    Column("confidence_score", Float, nullable=False, default=0.0),
    Column(
        "status",
        SAEnum(
            RumorStatus,
            name="rumor_status",
            values_callable=lambda enum: [value.value for value in enum],
            create_type=False,
        ),
        nullable=False,
        default=RumorStatus.NEW,
    ),
    Column("tags", ARRAY(String(100)), nullable=False, default=list),
    Column("event_candidate_payload", JSONB, nullable=False, default=dict),
    Column("event_id", PG_UUID(as_uuid=True), nullable=True),
    Column("is_public", Boolean, nullable=False, default=False),
    Column("published_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_rumors_source", "source_id"),
    Index("ix_rumors_publication", "raw_publication_id"),
    Index("ix_rumors_status", "status"),
    Index("ix_rumors_event", "event_id"),
    Index("ix_rumors_is_public", "is_public"),
    Index("ix_rumors_confidence", "confidence_score"),
    Index("ix_rumors_created_at", "created_at"),
)

__all__ = ["rumors_table"]
