"""DTO для игрока"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class PlayerDTO:
    """DTO для передачи данных игрока"""

    id: UUID
    name: str
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: date
    nationality: str
    position: str
    preferred_foot: str
    height_cm: int
    weight_kg: int
    current_club_id: Optional[UUID]
    current_league_id: Optional[UUID]
    market_value: Optional[Decimal]
    contract_until: Optional[date]
    shirt_number: Optional[int]
    age: int
    appearances: int = field(default=0)
    goals: int = field(default=0)
    assists: int = field(default=0)
    minutes_played: int = field(default=0)
    xg: float = field(default=0.0)
    xa: float = field(default=0.0)
    xg_per_90: float = field(default=0.0)
    xa_per_90: float = field(default=0.0)
    league_strength_coefficient: float = field(default=1.0)
