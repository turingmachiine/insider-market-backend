"""Pydantic схемы для shadow team"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ShadowTeamCandidateResponse(BaseModel):
    """Кандидат для shadow-team"""

    player_id: UUID
    player_name: str
    position: str
    club_name: str
    league_name: str
    age: int
    nationality: str
    market_value: Optional[Decimal] = None
    improvement_score: float
    key_stats: dict


class ShadowTeamResponse(BaseModel):
    """Shadow team"""

    team_id: UUID
    team_name: str
    candidates: dict[str, list[ShadowTeamCandidateResponse]]
    total_improvement_score: float
