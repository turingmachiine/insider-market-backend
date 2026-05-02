"""Таблица матчей"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.nsi_service.core.utils import utc_now
from src.backend.nsi_service.infrastructure.db.metadata import mapper_registry

matches_table = Table(
    "matches",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column(
        "home_club_id", PG_UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False
    ),
    Column(
        "away_club_id", PG_UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False
    ),
    Column("league_id", PG_UUID(as_uuid=True), ForeignKey("leagues.id"), nullable=True),
    Column("match_date", DateTime(timezone=True), nullable=False),
    Column("home_score", Integer, nullable=True),
    Column("away_score", Integer, nullable=True),
    Column("season", String(50), nullable=False),
    Column("round", String(50), nullable=True),
    Column("venue", String(255), nullable=True),
    Column("attendance", Integer, nullable=True),
    Column("status", String(50), nullable=False, default="scheduled"),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_matches_date", "match_date"),
    Index("ix_matches_league", "league_id"),
    Index("ix_matches_clubs", "home_club_id", "away_club_id"),
)


__all__ = ["matches_table"]
