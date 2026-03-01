from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from src.domain.interfaces.transaction_manager import TransactionManager


class SQLAlchemyTransactionManager(TransactionManager):
    """
    Реализация TransactionManager для SQLAlchemy с поддержкой вложенных транзакций
    Сессия передается извне (из DI)
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация с уже созданной сессией

        Args:
            session: Сессия SQLAlchemy из DI контейнера
        """
        self._session = session
        self._transaction: AsyncSessionTransaction | None = None
        self._savepoints: list[AsyncSessionTransaction] = []

    async def begin(self) -> None:
        """Начинает транзакцию"""
        if self.in_transaction:
            return
        self._transaction = await self._session.begin()

    async def begin_nested(self) -> None:
        """Начинает вложенную транзакцию (savepoint)"""
        if not self.in_transaction:
            # Если нет активной транзакции, начинаем новую
            self._transaction = await self._session.begin()

        # Создаем savepoint
        nested_savepoint = await self._session.begin_nested()
        self._savepoints.append(nested_savepoint)

    async def commit(self) -> None:
        """Подтверждает транзакцию"""
        if self._savepoints:
            nested_savepoint = self._savepoints.pop()
            await nested_savepoint.commit()
        elif self._transaction:
            await self._transaction.commit()
            self._transaction = None

    async def rollback(self) -> None:
        """Откатывает транзакцию"""
        if self._savepoints:
            nested_savepoint = self._savepoints.pop()
            await nested_savepoint.rollback()
        elif self._transaction:
            await self._transaction.rollback()
            self._transaction = None

    async def flush(self) -> None:
        """Принудительно применяет изменения к БД без коммита"""
        await self._session.flush()

    @property
    def in_transaction(self) -> bool:
        """Проверяет, есть ли активная транзакция"""
        return self._transaction is not None

    @property
    def in_nested(self) -> bool:
        """Проверяет, находимся ли во вложенной транзакции"""
        return bool(self._savepoints)
