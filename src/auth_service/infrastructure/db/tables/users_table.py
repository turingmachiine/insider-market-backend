from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.auth_service.infrastructure.db.metadata import mapper_registry

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("email", String(320), nullable=False, unique=True, index=True),
    Column("password_hash", String(255), nullable=False),
    Column("is_active", Boolean(), nullable=False, server_default=text("true")),
    Column(
        "failed_login_attempts",
        Integer(),
        nullable=False,
        server_default=text("0"),
    ),
    Column("locked_until", DateTime(timezone=True), nullable=True),
    Column("password_changed_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

__all__ = ["users_table"]
