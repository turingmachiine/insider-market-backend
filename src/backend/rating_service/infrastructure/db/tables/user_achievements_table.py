from sqlalchemy import Column, DateTime, Index, Numeric, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.rating_service.core.utils.datetime_utils import utc_now
from src.backend.rating_service.infrastructure.db.metadata import mapper_registry

user_achievements_table = Table(
    "rating_user_achievements",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column("achievement_code", String(100), nullable=False),
    Column("reward_amount", Numeric(20, 6), nullable=False),
    Column("awarded_at", DateTime(timezone=True), default=utc_now, nullable=False),
    UniqueConstraint(
        "user_id",
        "achievement_code",
        name="uq_rating_user_achievements_user_code",
    ),
    Index("ix_rating_user_achievements_user_id", "user_id"),
)

__all__ = ["user_achievements_table"]
