from sqlalchemy import Column, DateTime, Enum, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.admin_service.core.utils.datetime_utils import utc_now
from src.admin_service.domain.entities import AdminActionType
from src.admin_service.infrastructure.db.metadata import mapper_registry

admin_actions_table = Table(
    "admin_actions",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("actor_user_id", PG_UUID(as_uuid=True), nullable=True),
    Column(
        "action_type",
        Enum(
            AdminActionType,
            name="admin_action_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=False,
        ),
        nullable=False,
    ),
    Column("entity_type", String(50), nullable=False),
    Column("entity_id", String(100), nullable=False),
    Column("summary", String(200), nullable=False),
    Column("payload", JSONB(), nullable=True),
    Column("before", JSONB(), nullable=True),
    Column("after", JSONB(), nullable=True),
    Column("correlation_id", String(100), nullable=True, index=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
)

__all__ = ["admin_actions_table"]
