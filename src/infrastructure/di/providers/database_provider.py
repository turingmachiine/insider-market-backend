from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.core.config import Settings
from src.domain.interfaces.transaction_manager import TransactionManager
from src.infrastructure.db.database import create_engine, create_session_factory
from src.infrastructure.db.transaction_manager import SQLAlchemyTransactionManager


class DatabaseProvider(Provider):
    """Провайдер зависимостей базы данных"""

    scope = Scope.APP

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

    @provide
    def provide_settings(self) -> Settings:
        """Предоставление настроек"""
        return self.settings

    @provide
    async def provide_engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        """Создание движка базы данных"""
        engine = create_engine(settings)
        yield engine
        await engine.dispose()

    @provide
    def provide_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Фабрика сессий"""
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """Сессия базы данных (Scope.REQUEST)"""
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @provide(scope=Scope.REQUEST)
    async def provide_transaction_manager(
        self, session: AsyncSession
    ) -> TransactionManager:
        """Менеджер транзакции (Scope.REQUEST)"""
        return SQLAlchemyTransactionManager(session=session)
