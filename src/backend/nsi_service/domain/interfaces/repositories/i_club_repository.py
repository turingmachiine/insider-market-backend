from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.backend.nsi_service.domain.entities.club import Club


class IClubRepository(ABC):
    """Интерфейс репозитория клубов"""

    @abstractmethod
    async def get_by_id(self, club_id: UUID) -> Optional[Club]:
        """Получить клуб по ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Club]:
        """Поиск клуба по имени"""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Club]:
        """Получить все клубы с пагинацией"""
        pass

    @abstractmethod
    async def get_by_league(self, league_id: UUID, limit: int = 50) -> list[Club]:
        """Получить клубы лиги"""
        pass

    @abstractmethod
    async def save(self, club: Club) -> Club:
        """Сохранить клуб"""
        pass
