"""DTO для создания лиги"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class CreateLeagueDTO:
    """DTO для создания лиги"""

    name: str
    short_name: Optional[str] = None
    country: str = ""
    tier: int = 1
    confederation: str = "UEFA"
    logo_url: Optional[str] = None
    strength_coefficient: float = 1.0
    current_season: Optional[str] = None
    season_start: Optional[date] = None
    season_end: Optional[date] = None
