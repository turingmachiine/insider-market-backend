"""Клиент для Transfermarkt"""

from typing import Any

from src.backend.nsi_service.core.config import Settings
from src.backend.nsi_service.infrastructure.api_clients.base_client import (
    BaseStatsClient,
)


class TransfermarktClient(BaseStatsClient):
    """Клиент для Transfermarkt"""

    def __init__(self, settings: Settings):
        super().__init__(settings.TRANSFERMARKT_BASE_URL)
        self.settings = settings

    async def get_player_stats(self, player_id: str) -> dict[str, Any]:
        """
        Получить данные игрока с Transfermarkt.

        Transfermarkt не имеет публичного API.
        В продакшене требуется proper scraping.
        """
        return {
            "source": "transfermarkt",
            "player_id": player_id,
            "data": {
                "market_value": "50000000",
                "contract_until": "2027-06-30",
            },
        }

    async def get_club_stats(self, club_id: str) -> dict[str, Any]:
        """Получить данные клуба"""
        return {"source": "transfermarkt", "club_id": club_id, "data": {}}

    async def search_players(self, query: str) -> list[dict[str, Any]]:
        """Поиск игроков"""
        return []
