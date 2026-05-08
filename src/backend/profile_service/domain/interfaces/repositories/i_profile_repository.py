from abc import ABC, abstractmethod
from uuid import UUID

from src.backend.profile_service.domain.entities import Profile


class IProfileRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Profile]:
        pass

    @abstractmethod
    async def count_all(self) -> int:
        pass

    @abstractmethod
    async def save(self, profile: Profile) -> Profile:
        pass
