"""Таблица трансферов"""

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, Numeric, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.infrastructure.db.metadata import mapper_registry

transfers_table = Table(
    "transfers",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "player_id", PG_UUID(as_uuid=True), ForeignKey("players.id"), nullable=False
    ),
    Column(
        "from_club_id", PG_UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=True
    ),
    Column("to_club_id", PG_UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False),
    Column("transfer_date", Date, nullable=False),
    Column("transfer_fee", Numeric(15, 2), nullable=True),
    Column("transfer_type", String(50), nullable=False),
    Column("season", String(50), nullable=False),
    Index("ix_transfers_player", "player_id"),
    Index("ix_transfers_date", "transfer_date"),
)


__all__ = ["transfers_table"]
