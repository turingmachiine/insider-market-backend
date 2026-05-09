from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.nsi_service.application.dto import ShadowTeamDTO


class IShadowTeamService(ABC):
    """Интерфейс сервиса shadow-team"""

    @abstractmethod
    async def build_shadow_team(
        self, team_id: UUID, budget: Optional[float] = None
    ) -> Optional[ShadowTeamDTO]:
        """Построить shadow-team для усиления состава"""
        pass
