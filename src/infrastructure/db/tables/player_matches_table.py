"""Таблица выступлений игроков в матчах"""

from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.infrastructure.db.metadata import mapper_registry

player_matches_table = Table(
    "player_matches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "player_id", PG_UUID(as_uuid=True), ForeignKey("players.id"), nullable=False
    ),
    Column("match_id", PG_UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False),
    Column("club_id", PG_UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False),
    Column("position", String(50), nullable=False),
    Column("minutes_played", Integer, nullable=False, default=0),
    Column("goals", Integer, nullable=False, default=0),
    Column("assists", Integer, nullable=False, default=0),
    Column("yellow_cards", Integer, nullable=False, default=0),
    Column("red_cards", Integer, nullable=False, default=0),
    Column("xg", Float, nullable=False, default=0.0),
    Column("xa", Float, nullable=False, default=0.0),
    Column("rating", Float, nullable=True),
    Index("ix_player_matches_player", "player_id"),
    Index("ix_player_matches_match", "match_id"),
)


__all__ = ["player_matches_table"]
