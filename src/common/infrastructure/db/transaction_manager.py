from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from src.common.domain.interfaces import TransactionManager


class SQLAlchemyTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._transaction: AsyncSessionTransaction | None = None
        self._savepoints: list[AsyncSessionTransaction] = []

    async def begin(self) -> None:
        if self.in_transaction:
            return
        self._transaction = await self._session.begin()

    async def begin_nested(self) -> None:
        if not self.in_transaction:
            self._transaction = await self._session.begin()
        nested_savepoint = await self._session.begin_nested()
        self._savepoints.append(nested_savepoint)

    async def commit(self) -> None:
        if self._savepoints:
            nested_savepoint = self._savepoints.pop()
            await nested_savepoint.commit()
        elif self._transaction:
            await self._transaction.commit()
            self._transaction = None

    async def rollback(self) -> None:
        if self._savepoints:
            nested_savepoint = self._savepoints.pop()
            await nested_savepoint.rollback()
        elif self._transaction:
            await self._transaction.rollback()
            self._transaction = None

    async def flush(self) -> None:
        await self._session.flush()

    @property
    def in_transaction(self) -> bool:
        return self._transaction is not None

    @property
    def in_nested(self) -> bool:
        return bool(self._savepoints)


__all__ = ["SQLAlchemyTransactionManager"]
