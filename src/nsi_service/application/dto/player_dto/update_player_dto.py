from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class UpdatePlayerDTO:
    """DTO для обновления игрока"""

    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    position: Optional[str] = None
    preferred_foot: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    current_club_id: Optional[UUID] = None
    current_league_id: Optional[UUID] = None
    market_value: Optional[Decimal] = None
    contract_until: Optional[date] = None
    shirt_number: Optional[int] = None
