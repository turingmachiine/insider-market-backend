"""Фабрика клиентов статистических платформ"""

from src.nsi_service.core.config import Settings
from src.nsi_service.infrastructure.api_clients.base_client import BaseStatsClient


class StatsClientFactory:
    """Фабрика клиентов статистических платформ"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._clients: dict[str, BaseStatsClient] = {}

    def get_client(self, source: str) -> BaseStatsClient:
        """Получить клиент для источника"""
        if source not in self._clients:
            raise ValueError(f"Unknown stats source: {source}")
        return self._clients[source]

    async def close_all(self) -> None:
        """Закрыть все клиенты"""
        for client in self._clients.values():
            await client.close()
