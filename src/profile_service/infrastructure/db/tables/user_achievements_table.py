from sqlalchemy import Column, DateTime, Index, Integer, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.profile_service.core.utils.datetime_utils import utc_now
from src.profile_service.infrastructure.db.metadata import mapper_registry

user_achievements_table = Table(
    "user_achievements",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column("achievement_code", String(100), nullable=False),
    Column("progress", Integer, nullable=False),
    Column("awarded_at", DateTime(timezone=True), default=utc_now, nullable=False),
    UniqueConstraint(
        "user_id",
        "achievement_code",
        name="uq_user_achievements_user_code",
    ),
    Index("ix_user_achievements_user_id", "user_id"),
)

__all__ = ["user_achievements_table"]
