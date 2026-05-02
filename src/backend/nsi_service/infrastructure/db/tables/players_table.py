"""Таблица игроков"""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.nsi_service.core.utils import utc_now
from src.backend.nsi_service.domain.value_objects.position import Position
from src.backend.nsi_service.infrastructure.db.metadata import mapper_registry

players_table = Table(
    "players",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("first_name", String(100), nullable=True),
    Column("last_name", String(100), nullable=True),
    Column("date_of_birth", Date, nullable=False),
    Column("nationality", String(100), nullable=False),
    Column("position", Enum(Position, native_enum=False), nullable=False),
    Column("preferred_foot", String(20), nullable=False, default="right"),
    Column("height_cm", Integer, nullable=False),
    Column("weight_kg", Integer, nullable=False),
    Column(
        "current_club_id", PG_UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=True
    ),
    Column(
        "current_league_id",
        PG_UUID(as_uuid=True),
        ForeignKey("leagues.id"),
        nullable=True,
    ),
    Column("market_value", Numeric(15, 2), nullable=True),
    Column("contract_until", Date, nullable=True),
    Column("shirt_number", Integer, nullable=True),
    Column("appearances", Integer, nullable=False, default=0),
    Column("goals", Integer, nullable=False, default=0),
    Column("assists", Integer, nullable=False, default=0),
    Column("yellow_cards", Integer, nullable=False, default=0),
    Column("red_cards", Integer, nullable=False, default=0),
    Column("minutes_played", Integer, nullable=False, default=0),
    Column("xg", Float, nullable=False, default=0.0),
    Column("xa", Float, nullable=False, default=0.0),
    Column("xg_per_90", Float, nullable=False, default=0.0),
    Column("xa_per_90", Float, nullable=False, default=0.0),
    Column("league_strength_coefficient", Float, nullable=False, default=1.0),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_players_name", "name"),
    Index("ix_players_position", "position"),
    Index("ix_players_club", "current_club_id"),
    Index("ix_players_league", "current_league_id"),
    Index("ix_players_nationality", "nationality"),
)


__all__ = ["players_table"]
