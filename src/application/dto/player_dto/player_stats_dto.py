from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class PlayerStatsDTO:
    """DTO для статистики игрока"""

    player_id: UUID
    player_name: str
    position: str
    appearances: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    minutes_played: int
    goals_per_90: float
    assists_per_90: float
    xg: float
    xa: float
    xg_per_90: float
    xa_per_90: float
    league_strength_coefficient: float
