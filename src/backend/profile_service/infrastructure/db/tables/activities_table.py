from sqlalchemy import Column, DateTime, Index, String, Table, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.profile_service.core.utils.datetime_utils import utc_now
from src.backend.profile_service.domain.entities import ActivityType
from src.backend.profile_service.infrastructure.db.metadata import mapper_registry

activity_type_enum = ENUM(
    ActivityType,
    name="profile_activity_type",
    values_callable=lambda enum_cls: [item.value for item in enum_cls],
    create_type=False,
)

activities_table = Table(
    "activities",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("user_id", PG_UUID(as_uuid=True), nullable=False),
    Column("activity_type", activity_type_enum, nullable=False),
    Column("title", String(200), nullable=False),
    Column("description", Text(), nullable=True),
    Column("payload", JSONB, nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Index("ix_activities_user_id", "user_id"),
    Index("ix_activities_activity_type", "activity_type"),
    Index("ix_activities_created_at", "created_at"),
)

__all__ = ["activities_table", "activity_type_enum"]
