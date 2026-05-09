from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.rating_service.core.utils.datetime_utils import utc_now
from src.rating_service.domain.entities import UserStatus
from src.rating_service.infrastructure.db.metadata import mapper_registry

rating_profiles_table = Table(
    "rating_profiles",
    mapper_registry.metadata,
    Column("user_id", PG_UUID(as_uuid=True), primary_key=True),
    Column("rating", Integer(), nullable=False),
    Column("xp", Integer(), nullable=False),
    Column("level", Integer(), nullable=False),
    Column(
        "status",
        ENUM(
            UserStatus,
            name="rating_user_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=False,
        ),
        nullable=False,
    ),
    Column("total_predictions", Integer(), nullable=False),
    Column("correct_predictions", Integer(), nullable=False),
    Column("current_streak", Integer(), nullable=False),
    Column("best_streak", Integer(), nullable=False),
    Column("markets_created", Integer(), nullable=False),
    Column("analyses_published", Integer(), nullable=False),
    Column("comments_posted", Integer(), nullable=False),
    Column("active_days", Integer(), nullable=False),
    Column("settled_stake", Numeric(20, 6), nullable=False),
    Column("settled_payout", Numeric(20, 6), nullable=False),
    Column("last_activity_date", Date(), nullable=True),
    Column("last_event_at", DateTime(timezone=True), nullable=True),
    Column("last_calculated_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_rating_profiles_rating", "rating"),
    Index("ix_rating_profiles_status", "status"),
)

__all__ = ["rating_profiles_table"]
