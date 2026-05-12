from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.auth_service.infrastructure.db.metadata import mapper_registry

refresh_tokens_table = Table(
    "refresh_tokens",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column(
        "user_id",
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("token_hash", String(64), nullable=False, unique=True, index=True),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("revoked_at", DateTime(timezone=True), nullable=True),
    Column("replaced_by_token_id", PG_UUID(as_uuid=True), nullable=True),
)

__all__ = ["refresh_tokens_table"]
