from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Table, Text
from sqlalchemy.dialects.postgresql import ENUM

from src.rating_service.core.utils.datetime_utils import utc_now
from src.rating_service.domain.entities import AchievementRarity
from src.rating_service.infrastructure.db.metadata import mapper_registry

achievement_definitions_table = Table(
    "rating_achievement_definitions",
    mapper_registry.metadata,
    Column("code", String(100), primary_key=True),
    Column("name", String(200), nullable=False),
    Column("description", Text(), nullable=False),
    Column("metric", String(100), nullable=False),
    Column("threshold", Integer(), nullable=False),
    Column("reward_amount", Numeric(20, 6), nullable=False),
    Column(
        "rarity",
        ENUM(
            AchievementRarity,
            name="rating_achievement_rarity",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            create_type=False,
        ),
        nullable=False,
    ),
    Column("is_active", Boolean(), nullable=False),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
)

__all__ = ["achievement_definitions_table"]
