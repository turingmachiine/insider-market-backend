from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class SimilarPlayerDTO:
    """DTO для похожего игрока"""

    player_id: UUID
    player_name: str
    position: str
    club_name: str
    league_name: str
    age: int
    nationality: str
    similarity_score: float
    market_value: Optional[Decimal]
    key_stats: dict
