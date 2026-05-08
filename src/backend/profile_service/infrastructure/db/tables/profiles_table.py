from sqlalchemy import Column, DateTime, Index, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.profile_service.core.utils.datetime_utils import utc_now
from src.backend.profile_service.infrastructure.db.metadata import mapper_registry

profiles_table = Table(
    "profiles",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False, unique=True),
    Column("display_name", String(120), nullable=False),
    Column("bio", Text(), nullable=True),
    Column("avatar_url", String(1000), nullable=True),
    Column("favorite_club", String(200), nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_profiles_user_id", "user_id", unique=True),
)

__all__ = ["profiles_table"]
