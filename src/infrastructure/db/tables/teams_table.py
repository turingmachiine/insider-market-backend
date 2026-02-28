"""Таблица команд"""

from sqlalchemy import Column, DateTime, Index, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.core.utils import utc_now
from src.infrastructure.db.metadata import mapper_registry

teams_table = Table(
    "teams",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column("description", Text, nullable=True),
    Column("squad", JSONB, nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_teams_user", "user_id"),
    Index("ix_teams_name", "name"),
)


__all__ = ["teams_table"]
