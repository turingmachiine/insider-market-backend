from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.rumor_service.core.utils.datetime_utils import utc_now
from src.backend.rumor_service.infrastructure.db.metadata import mapper_registry

raw_publications_table = Table(
    "raw_publications",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column(
        "source_id",
        PG_UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("external_id", String(255), nullable=True),
    Column("url", String(500), nullable=True),
    Column("text", Text, nullable=False),
    Column("published_at", DateTime(timezone=True), nullable=True),
    Column("collected_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column("payload", JSONB, nullable=False, default=dict),
    Index("ix_raw_publications_source", "source_id"),
    Index("ix_raw_publications_external", "source_id", "external_id", unique=True),
    Index("ix_raw_publications_published_at", "published_at"),
)

__all__ = ["raw_publications_table"]
