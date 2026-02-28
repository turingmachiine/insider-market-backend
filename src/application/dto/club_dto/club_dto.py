"""DTO для клуба"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class ClubDTO:
    """DTO для передачи данных клуба"""

    id: UUID
    name: str
    short_name: Optional[str]
    founded_year: Optional[int]
    country: str
    city: str
    stadium_name: Optional[str]
    stadium_capacity: Optional[int]
    league_id: Optional[UUID]
    logo_url: Optional[str]
    website: Optional[str]
    squad_market_value: Optional[Decimal]
    average_age: Optional[float]
    foreign_players_count: Optional[int]
    national_team_players_count: Optional[int]
