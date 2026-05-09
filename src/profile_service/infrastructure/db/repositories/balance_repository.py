from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile_service.domain.entities import BalanceTransaction, UserBalance
from src.profile_service.domain.interfaces.repositories import IBalanceRepository
from src.profile_service.infrastructure.db.tables import (
    balance_transactions_table,
    user_balances_table,
)


class BalanceRepository(IBalanceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.balance_model = UserBalance
        self.transaction_model = BalanceTransaction

    async def get_by_user_id(self, user_id: UUID) -> UserBalance | None:
        query = select(self.balance_model).where(
            user_balances_table.c.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def save(self, balance: UserBalance) -> UserBalance:
        self.session.add(balance)
        await self.session.flush()
        return balance

    async def save_transaction(
        self,
        transaction: BalanceTransaction,
    ) -> BalanceTransaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_transactions(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BalanceTransaction]:
        query = (
            select(self.transaction_model)
            .where(balance_transactions_table.c.user_id == user_id)
            .order_by(balance_transactions_table.c.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_transaction_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> BalanceTransaction | None:
        query = select(self.transaction_model).where(
            balance_transactions_table.c.idempotency_key == idempotency_key
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
