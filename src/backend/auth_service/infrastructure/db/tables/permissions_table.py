from uuid import uuid4

from sqlalchemy import Column, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.auth_service.infrastructure.db.metadata import mapper_registry

permissions_table = Table(
    "permissions",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("name", String(150), nullable=False, unique=True, index=True),
)

__all__ = ["permissions_table"]
