"""Порты (интерфейсы) для application слоя"""

from .player_service import IPlayerService
from .shadow_team_service import IShadowTeamService

__all__ = [
    "IPlayerService",
    "IShadowTeamService",
]
