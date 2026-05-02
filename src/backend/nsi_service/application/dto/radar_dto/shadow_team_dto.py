from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.backend.nsi_service.application.dto.radar_dto import ShadowTeamCandidateDTO


@dataclass
class ShadowTeamDTO:
    """Shadow team для усиления состава"""

    team_id: UUID
    team_name: str
    candidates: dict[str, list[ShadowTeamCandidateDTO]]
    total_improvement_score: float
