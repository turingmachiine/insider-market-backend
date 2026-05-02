"""Таблица лиг"""

from sqlalchemy import Column, Date, DateTime, Float, Index, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.backend.nsi_service.core.utils import utc_now
from src.backend.nsi_service.infrastructure.db.metadata import mapper_registry

leagues_table = Table(
    "leagues",
    mapper_registry.metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("short_name", String(100), nullable=True),
    Column("country", String(100), nullable=False),
    Column("tier", Integer, nullable=False, default=1),
    Column("confederation", String(50), nullable=False, default="UEFA"),
    Column("logo_url", String(500), nullable=True),
    Column("strength_coefficient", Float, nullable=False, default=1.0),
    Column("current_season", String(50), nullable=True),
    Column("season_start", Date, nullable=True),
    Column("season_end", Date, nullable=True),
    Column("created_at", DateTime(timezone=True), default=utc_now, nullable=False),
    Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    ),
    Index("ix_leagues_country", "country"),
    Index("ix_leagues_tier", "tier"),
)


__all__ = ["leagues_table"]
