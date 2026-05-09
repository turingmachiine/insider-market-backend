from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rating_service.domain.entities import (
    RewardTransaction,
    RewardTransactionStatus,
)
from src.rating_service.domain.interfaces.repositories import IRewardRepository
from src.rating_service.infrastructure.db.tables import reward_transactions_table


class RewardRepository(IRewardRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = RewardTransaction

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> RewardTransaction | None:
        query = select(self.model).where(
            reward_transactions_table.c.idempotency_key == idempotency_key
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_pending(self, limit: int = 100) -> list[RewardTransaction]:
        query = (
            select(self.model)
            .where(
                reward_transactions_table.c.status.in_(
                    [
                        RewardTransactionStatus.PENDING,
                        RewardTransactionStatus.FAILED,
                    ]
                )
            )
            .order_by(
                reward_transactions_table.c.attempts,
                reward_transactions_table.c.created_at,
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, reward: RewardTransaction) -> RewardTransaction:
        self.session.add(reward)
        await self.session.flush()
        return reward
