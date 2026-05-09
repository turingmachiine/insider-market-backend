from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncIterator


class TransactionManager(ABC):
    @abstractmethod
    async def begin(self) -> None:
        pass

    @abstractmethod
    async def begin_nested(self) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def flush(self) -> None:
        pass

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["TransactionManager"]:
        await self.begin()
        try:
            yield self
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    @asynccontextmanager
    async def nested_transaction(self) -> AsyncIterator["TransactionManager"]:
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


__all__ = ["TransactionManager"]
