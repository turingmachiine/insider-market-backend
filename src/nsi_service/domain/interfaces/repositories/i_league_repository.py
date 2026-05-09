from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.nsi_service.domain.entities.league import League


class ILeagueRepository(ABC):
    """Интерфейс репозитория лиг"""

    @abstractmethod
    async def get_by_id(self, league_id: UUID) -> Optional[League]:
        """Получить лигу по ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[League]:
        """Поиск лиги по имени"""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 50, offset: int = 0) -> list[League]:
        """Получить все лиги с пагинацией"""
        pass

    @abstractmethod
    async def get_top_leagues(self, limit: int = 10) -> list[League]:
        """Получить топ лиги"""
        pass

    @abstractmethod
    async def save(self, league: League) -> League:
        """Сохранить лигу"""
        pass
