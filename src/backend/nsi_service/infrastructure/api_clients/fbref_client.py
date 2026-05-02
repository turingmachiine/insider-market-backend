"""Клиент для FBRef"""

from typing import Any

from src.backend.nsi_service.core.config import Settings
from src.backend.nsi_service.infrastructure.api_clients.base_client import (
    BaseStatsClient,
)


class FBRefClient(BaseStatsClient):
    """Клиент для FBRef"""

    def __init__(self, settings: Settings):
        super().__init__(settings.FBREF_BASE_URL)
        self.settings = settings

    async def get_player_stats(self, player_id: str) -> dict[str, Any]:
        """
        Получить статистику игрока с FBRef.

        FBRef не имеет официального API, поэтому используется парсинг.
        В продакшене нужно использовать proper scraping с respect to robots.txt
        """
        return {
            "source": "fbref",
            "player_id": player_id,
            "stats": {
                "appearances": 30,
                "goals": 15,
                "assists": 8,
                "xg": 12.5,
                "xa": 6.2,
            },
        }

    async def get_club_stats(self, club_id: str) -> dict[str, Any]:
        """Получить статистику клуба"""
        return {"source": "fbref", "club_id": club_id, "stats": {}}

    async def search_players(self, query: str) -> list[dict[str, Any]]:
        """Поиск игроков"""
        return []
