from sqlalchemy import Column, DateTime, String, Table, Text

from src.backend.profile_service.core.utils.datetime_utils import utc_now
from src.backend.profile_service.infrastructure.db.metadata import mapper_registry

achievements_table = Table(
    "achievements",
    mapper_registry.metadata,
    Column("code", String(100), primary_key=True),
    Column("name", String(200), nullable=False),
    Column("description", Text(), nullable=False),
    Column("icon_url", String(1000), nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
)

__all__ = ["achievements_table"]
