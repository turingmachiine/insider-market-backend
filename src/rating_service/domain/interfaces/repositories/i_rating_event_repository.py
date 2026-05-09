from abc import ABC, abstractmethod

from src.rating_service.domain.entities import RatingEvent


class IRatingEventRepository(ABC):
    @abstractmethod
    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> RatingEvent | None:
        raise NotImplementedError

    @abstractmethod
    async def get_unprocessed(self, limit: int = 100) -> list[RatingEvent]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, event: RatingEvent) -> RatingEvent:
        raise NotImplementedError
