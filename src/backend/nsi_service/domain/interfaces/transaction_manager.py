from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncIterator


class TransactionManager(ABC):
    """
    Асинхронный интерфейс менеджера транзакций
    """

    @abstractmethod
    async def begin(self) -> None:
        """Начинает транзакцию асинхронно"""
        pass

    @abstractmethod
    async def begin_nested(self) -> None:
        """Начинает вложенную транзакцию (savepoint) асинхронно"""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Подтверждает транзакцию асинхронно"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Откатывает транзакцию асинхронно"""
        pass

    @abstractmethod
    async def flush(self) -> None:
        """Принудительно применяет изменения к БД без коммита"""
        pass

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["TransactionManager"]:
        """
        Асинхронный контекстный менеджер для транзакции
        """
        await self.begin()
        try:
            yield self
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    @asynccontextmanager
    async def nested_transaction(self) -> AsyncIterator["TransactionManager"]:
        """
        Асинхронный контекстный менеджер для вложенной транзакции (savepoint)
        """
        await self.begin_nested()
        try:
            yield self
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    @property
    @abstractmethod
    def in_transaction(self) -> bool:
        pass

    @property
    @abstractmethod
    def in_nested(self) -> bool:
        pass
