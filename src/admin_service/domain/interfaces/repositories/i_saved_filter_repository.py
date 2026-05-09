from abc import ABC, abstractmethod
from uuid import UUID

from src.admin_service.domain.entities import SavedFilter


class ISavedFilterRepository(ABC):
    @abstractmethod
    async def get_filters(
        self,
        actor_user_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SavedFilter]:
        raise NotImplementedError

    @abstractmethod
    async def count_filters(
        self,
        actor_user_id: UUID | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def save(self, saved_filter: SavedFilter) -> SavedFilter:
        raise NotImplementedError
