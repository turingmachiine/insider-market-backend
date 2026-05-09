from abc import ABC, abstractmethod
from uuid import UUID

from src.profile_service.domain.entities import BalanceTransaction, UserBalance


class IBalanceRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserBalance | None:
        pass

    @abstractmethod
    async def save(self, balance: UserBalance) -> UserBalance:
        pass

    @abstractmethod
    async def save_transaction(
        self,
        transaction: BalanceTransaction,
    ) -> BalanceTransaction:
        pass

    @abstractmethod
    async def get_transactions(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BalanceTransaction]:
        pass

    @abstractmethod
    async def get_transaction_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> BalanceTransaction | None:
        pass
