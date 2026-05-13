from abc import ABC, abstractmethod

from src.auth_service.domain.entities import Permission


class IPermissionRepository(ABC):
    """Интерфейс репозитория permissions."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Permission | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Permission]:
        pass

    @abstractmethod
    async def create(self, name: str) -> Permission:
        pass
