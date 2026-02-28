from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.team import Team


class ITeamRepository(ABC):
    """Интерфейс репозитория команд пользователей"""

    @abstractmethod
    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Получить команду по ID"""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[Team]:
        """Получить команды пользователя"""
        pass

    @abstractmethod
    async def save(self, team: Team) -> Team:
        """Сохранить команду"""
        pass

    @abstractmethod
    async def delete_by_id(self, team_id: UUID) -> bool:
        """Удалить команду"""
        pass

    @abstractmethod
    async def delete(self, team: Team) -> bool:
        """Удалить команду"""
        pass
