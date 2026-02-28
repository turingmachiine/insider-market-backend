"""Таблица сырых данных"""

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.core.utils import utc_now
from src.infrastructure.db.metadata import mapper_registry

raw_stats_table = Table(
    "raw_stats",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source", String(50), nullable=False),
    Column("entity_type", String(50), nullable=False),
    Column("entity_id", PG_UUID(as_uuid=True), nullable=False),
    Column("data", String, nullable=False),
    Column("fetched_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column("processed", Boolean, default=False, nullable=False),
    Index("ix_raw_stats_source", "source"),
    Index("ix_raw_stats_entity", "entity_type", "entity_id"),
    Index("ix_raw_stats_processed", "processed"),
)


__all__ = ["raw_stats_table"]
