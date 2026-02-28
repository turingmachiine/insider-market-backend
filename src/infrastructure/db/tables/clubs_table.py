"""Таблица клубов"""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.core.utils.datetime_utils import utc_now
from src.infrastructure.db.metadata import mapper_registry

clubs_table = Table(
    "clubs",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("short_name", String(100), nullable=True),
    Column("founded_year", Integer, nullable=True),
    Column("country", String(100), nullable=False),
    Column("city", String(100), nullable=False),
    Column("stadium_name", String(255), nullable=True),
    Column("stadium_capacity", Integer, nullable=True),
    Column("league_id", PG_UUID(as_uuid=True), ForeignKey("leagues.id"), nullable=True),
    Column("logo_url", String(500), nullable=True),
    Column("website", String(255), nullable=True),
    Column("squad_market_value", Numeric(15, 2), nullable=True),
    Column("average_age", Float, nullable=True),
    Column("foreign_players_count", Integer, nullable=True),
    Column("national_team_players_count", Integer, nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_clubs_name", "name"),
    Index("ix_clubs_league", "league_id"),
    Index("ix_clubs_country", "country"),
)


__all__ = ["clubs_table"]
