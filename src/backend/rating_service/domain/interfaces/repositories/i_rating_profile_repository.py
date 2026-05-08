from abc import ABC, abstractmethod
from uuid import UUID

from src.backend.rating_service.domain.entities import RatingProfile


class IRatingProfileRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> RatingProfile | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[RatingProfile]:
        raise NotImplementedError

    @abstractmethod
    async def count_all(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_leaderboard(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RatingProfile]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, profile: RatingProfile) -> RatingProfile:
        raise NotImplementedError
