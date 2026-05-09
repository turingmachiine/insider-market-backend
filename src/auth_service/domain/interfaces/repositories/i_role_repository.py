from abc import ABC, abstractmethod

from src.auth_service.domain.entities import Role, User


class IRoleRepository(ABC):
    """Интерфейс репозитория ролей."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        pass

    @abstractmethod
    async def ensure_with_permissions(
        self,
        role_name: str,
        permissions: list[str],
        user: User | None = None,
    ) -> Role:
        pass
