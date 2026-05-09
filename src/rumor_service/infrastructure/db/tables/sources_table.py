from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, Index, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.rumor_service.core.utils.datetime_utils import utc_now
from src.rumor_service.domain.entities import SourceType
from src.rumor_service.infrastructure.db.metadata import mapper_registry

sources_table = Table(
    "sources",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("name", String(255), nullable=False),
    Column(
        "source_type",
        SAEnum(
            SourceType,
            name="source_type",
            values_callable=lambda enum: [value.value for value in enum],
            create_type=False,
        ),
        nullable=False,
    ),
    Column("handle", String(255), nullable=True),
    Column("url", String(500), nullable=True),
    Column("weight", Float, nullable=False, default=1.0),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_sources_name", "name", unique=True),
    Index("ix_sources_type", "source_type"),
    Index("ix_sources_active", "is_active"),
)

__all__ = ["sources_table"]
