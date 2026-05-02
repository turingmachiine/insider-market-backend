from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class CreatePlayerDTO:
    """DTO для создания игрока"""

    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: str = ""
    position: str = ""
    preferred_foot: str = "right"
    height_cm: int = 180
    weight_kg: int = 75
    current_club_id: Optional[UUID] = None
    current_league_id: Optional[UUID] = None
    market_value: Optional[Decimal] = None
    contract_until: Optional[date] = None
    shirt_number: Optional[int] = None
