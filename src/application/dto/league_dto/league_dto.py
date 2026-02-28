"""DTO для лиги"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class LeagueDTO:
    """DTO для передачи данных лиги"""

    id: UUID
    name: str
    short_name: Optional[str]
    country: str
    tier: int
    confederation: str
    logo_url: Optional[str]
    strength_coefficient: float
    current_season: Optional[str]
    is_top_league: bool
