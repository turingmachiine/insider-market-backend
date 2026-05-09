"""DTO для создания клуба"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class CreateClubDTO:
    """DTO для создания клуба"""

    name: str
    short_name: Optional[str] = None
    founded_year: Optional[int] = None
    country: str = ""
    city: str = ""
    stadium_name: Optional[str] = None
    stadium_capacity: Optional[int] = None
    league_id: Optional[UUID] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    squad_market_value: Optional[Decimal] = None
    average_age: Optional[float] = None
    foreign_players_count: Optional[int] = None
    national_team_players_count: Optional[int] = None
