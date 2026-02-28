"""Pydantic схемы для лиг"""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LeagueBase(BaseModel):
    """Базовая схема лиги"""

    name: str = Field(..., min_length=1, max_length=255)
    short_name: Optional[str] = Field(None, max_length=100)
    country: str = Field(..., max_length=100)
    tier: int = Field(1, ge=1, le=10)
    confederation: str = Field("UEFA", max_length=50)


class LeagueCreate(LeagueBase):
    """Схема создания лиги"""

    logo_url: Optional[str] = None
    strength_coefficient: float = Field(1.0, ge=0.1, le=2.0)
    current_season: Optional[str] = None
    season_start: Optional[date] = None
    season_end: Optional[date] = None


class LeagueResponse(LeagueBase):
    """Схема ответа лиги"""

    model_config = {"from_attributes": True}

    id: UUID
    logo_url: Optional[str]
    strength_coefficient: float
    current_season: Optional[str]
    is_top_league: bool
