"""Pydantic схемы для клубов"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ClubBase(BaseModel):
    """Базовая схема клуба"""

    name: str = Field(..., min_length=1, max_length=255)
    short_name: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1850, le=2026)
    country: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)
    stadium_name: Optional[str] = Field(None, max_length=255)
    stadium_capacity: Optional[int] = Field(None, ge=0)
    logo_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=255)


class ClubCreate(ClubBase):
    """Схема создания клуба"""

    league_id: Optional[UUID] = None
    squad_market_value: Optional[Decimal] = None
    average_age: Optional[float] = Field(None, ge=16, le=40)
    foreign_players_count: Optional[int] = Field(None, ge=0)
    national_team_players_count: Optional[int] = Field(None, ge=0)


class ClubResponse(ClubBase):
    """Схема ответа клуба"""

    model_config = {"from_attributes": True}

    id: UUID
    league_id: Optional[UUID] = None
    squad_market_value: Optional[Decimal] = None
    average_age: Optional[float] = None
    foreign_players_count: Optional[int] = None
    national_team_players_count: Optional[int] = None
