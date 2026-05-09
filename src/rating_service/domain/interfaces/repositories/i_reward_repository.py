from abc import ABC, abstractmethod

from src.rating_service.domain.entities import RewardTransaction


class IRewardRepository(ABC):
    @abstractmethod
    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> RewardTransaction | None:
        raise NotImplementedError

    @abstractmethod
    async def get_pending(self, limit: int = 100) -> list[RewardTransaction]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, reward: RewardTransaction) -> RewardTransaction:
        raise NotImplementedError
