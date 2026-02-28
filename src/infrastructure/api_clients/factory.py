"""Фабрика клиентов статистических платформ"""

from src.core.config import Settings
from src.infrastructure.api_clients.base_client import BaseStatsClient
from src.infrastructure.api_clients.fbref_client import FBRefClient
from src.infrastructure.api_clients.transfermarkt_client import TransfermarktClient
from src.infrastructure.api_clients.understat_client import UnderstatClient


class StatsClientFactory:
    """Фабрика клиентов статистических платформ"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._clients: dict[str, BaseStatsClient] = {}

    def get_client(self, source: str) -> BaseStatsClient:
        """Получить клиент для источника"""
        if source not in self._clients:
            if source == "fbref":
                self._clients[source] = FBRefClient(self.settings)
            elif source == "transfermarkt":
                self._clients[source] = TransfermarktClient(self.settings)
            elif source == "understat":
                self._clients[source] = UnderstatClient(self.settings)
            else:
                raise ValueError(f"Unknown stats source: {source}")
        return self._clients[source]

    async def close_all(self) -> None:
        """Закрыть все клиенты"""
        for client in self._clients.values():
            await client.close()
