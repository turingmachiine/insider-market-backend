"""Базовый класс для клиентов статистических платформ"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class BaseStatsClient(ABC):
    """Базовый класс для клиентов статистических платформ"""

    def __init__(self, base_url: str, session: Optional[aiohttp.ClientSession] = None):
        self.base_url = base_url
        self._session = session
        self._own_session: Optional[aiohttp.ClientSession] = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Получить HTTP сессию"""
        if self._session:
            return self._session
        if not self._own_session:
            self._own_session = aiohttp.ClientSession()
        return self._own_session

    async def close(self) -> None:
        """Закрыть сессию"""
        if self._own_session:
            await self._own_session.close()
            self._own_session = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Выполнить HTTP запрос"""
        session = self._get_session()
        url = f"{self.base_url}{endpoint}"

        async with session.request(
            method,
            url,
            params=params,
            headers=headers,
        ) as response:
            if response.status != 200:
                logger.error(f"Request failed: {url}, status: {response.status}")
                raise aiohttp.ClientError(
                    f"Request failed with status {response.status}"
                )

            return await response.json()  # type: ignore[no-any-return]

    @abstractmethod
    async def get_player_stats(self, player_id: str) -> dict[str, Any]:
        """Получить статистику игрока"""
        pass

    @abstractmethod
    async def get_club_stats(self, club_id: str) -> dict[str, Any]:
        """Получить статистику клуба"""
        pass

    @abstractmethod
    async def search_players(self, query: str) -> list[dict[str, Any]]:
        """Поиск игроков"""
        pass
