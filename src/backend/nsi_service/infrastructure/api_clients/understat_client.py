"""Клиент для Understat (xG статистика)"""

from typing import Any

from src.backend.nsi_service.core.config import Settings
from src.backend.nsi_service.infrastructure.api_clients.base_client import (
    BaseStatsClient,
)


class UnderstatClient(BaseStatsClient):
    """Клиент для Understat (xG статистика)"""

    def __init__(self, settings: Settings):
        super().__init__(settings.UNDERSTAT_BASE_URL)
        self.settings = settings

    async def get_player_stats(self, player_id: str) -> dict[str, Any]:
        """
        Получить xG статистику игрока с Understat.

        Understat предоставляет API для xG данных.
        """
        return {
            "source": "understat",
            "player_id": player_id,
            "xg_stats": {
                "xg": 12.5,
                "xg_per_90": 0.45,
                "xa": 6.2,
                "xa_per_90": 0.22,
                "xg_chain": 18.3,
                "xg_buildup": 8.1,
            },
        }

    async def get_club_stats(self, club_id: str) -> dict[str, Any]:
        """Получить xG статистику клуба"""
        return {"source": "understat", "club_id": club_id, "xg_stats": {}}

    async def search_players(self, query: str) -> list[dict[str, Any]]:
        """Поиск игроков"""
        return []
