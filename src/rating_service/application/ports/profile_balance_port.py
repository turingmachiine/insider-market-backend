from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID


class ProfileBalancePort(ABC):
    @abstractmethod
    async def credit_achievement_reward(
        self,
        user_id: UUID,
        amount: Decimal,
        achievement_code: str,
        idempotency_key: str,
    ) -> None:
        raise NotImplementedError
