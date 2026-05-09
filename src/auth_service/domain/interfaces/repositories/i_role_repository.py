from abc import ABC, abstractmethod
from collections.abc import Iterable

from src.auth_service.domain.entities import Role, User
from src.common.domain.security import Permission
from src.common.domain.security import Role as AccessRole


class IRoleRepository(ABC):
    """Интерфейс репозитория ролей."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        pass

    @abstractmethod
    async def ensure_with_permissions(
        self,
        role_name: AccessRole | str,
        permissions: Iterable[Permission | str],
        user: User | None = None,
    ) -> Role:
        pass
