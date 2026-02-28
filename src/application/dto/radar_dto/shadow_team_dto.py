from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.application.dto.radar_dto.shadow_team_candidate_dto import (
    ShadowTeamCandidateDTO,
)


@dataclass
class ShadowTeamDTO:
    """Shadow team для усиления состава"""

    team_id: UUID
    team_name: str
    candidates: dict[str, list[ShadowTeamCandidateDTO]]
    total_improvement_score: float
