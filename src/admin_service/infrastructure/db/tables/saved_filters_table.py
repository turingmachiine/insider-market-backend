from sqlalchemy import Column, DateTime, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.admin_service.core.utils.datetime_utils import utc_now
from src.admin_service.infrastructure.db.metadata import mapper_registry

saved_filters_table = Table(
    "admin_saved_filters",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("actor_user_id", PG_UUID(as_uuid=True), nullable=False),
    Column("name", String(120), nullable=False),
    Column("scope", String(120), nullable=False),
    Column("criteria", JSONB(), nullable=False),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
)

__all__ = ["saved_filters_table"]
