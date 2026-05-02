from abc import ABC, abstractmethod
from uuid import UUID

from src.backend.auth_service.domain.entities import User


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    async def create(self, email: str, password_hash: str) -> User:
        pass
