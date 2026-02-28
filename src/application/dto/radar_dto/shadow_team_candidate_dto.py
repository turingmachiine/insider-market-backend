from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class ShadowTeamCandidateDTO:
    """Кандидат для shadow-team"""

    player_id: UUID
    player_name: str
    position: str
    club_name: str
    league_name: str
    age: int
    nationality: str
    market_value: Optional[Decimal]
    improvement_score: float
    key_stats: dict
