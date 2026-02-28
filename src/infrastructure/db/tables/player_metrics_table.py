"""Таблица метрик игроков"""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.core.utils import utc_now
from src.infrastructure.db.metadata import mapper_registry

player_metrics_table = Table(
    "player_metrics",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "player_id", PG_UUID(as_uuid=True), ForeignKey("players.id"), nullable=False
    ),
    Column("metric_name", String(100), nullable=False),
    Column("metric_value", Float, nullable=False),
    Column("percentile", Float, nullable=True),
    Column("league_average", Float, nullable=True),
    Column("position_average", Float, nullable=True),
    Column("calculated_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Index("ix_player_metrics_player", "player_id"),
    Index("ix_player_metrics_name", "metric_name"),
)


__all__ = ["player_metrics_table"]
