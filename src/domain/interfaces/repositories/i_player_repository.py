from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities import Player
from src.domain.value_objects import Position


class IPlayerRepository(ABC):
    """Интерфейс репозитория игроков"""

    @abstractmethod
    async def get_by_id(self, player_id: UUID) -> Optional[Player]:
        """Получить игрока по ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> list[Player]:
        """Поиск игроков по имени"""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Player]:
        """Получить всех игроков с пагинацией"""
        pass

    @abstractmethod
    async def get_by_position(
        self, position: Position, limit: int = 50
    ) -> list[Player]:
        """Получить игроков по позиции"""
        pass

    @abstractmethod
    async def get_by_league(self, league_id: UUID, limit: int = 100) -> list[Player]:
        """Получить игроков лиги"""
        pass

    @abstractmethod
    async def get_by_club(self, club_id: UUID, limit: int = 50) -> list[Player]:
        """Получить игроков клуба"""
        pass

    @abstractmethod
    async def save(self, player: Player) -> Player:
        """Сохранить игрока"""
        pass

    @abstractmethod
    async def delete(self, player: Player) -> bool:
        """Удалить игрока"""
        pass

    @abstractmethod
    async def delete_by_id(self, player_id: UUID) -> bool:
        """Удалить игрока"""
        pass
