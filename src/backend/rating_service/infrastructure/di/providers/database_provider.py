from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.backend.common.domain.interfaces import TransactionManager
from src.backend.common.infrastructure.db import SQLAlchemyTransactionManager
from src.backend.rating_service.core.config import RatingSettings
from src.backend.rating_service.infrastructure.db.database import (
    create_engine,
    create_session_factory,
)


class DatabaseProvider(Provider):
    scope = Scope.APP

    def __init__(self, settings: RatingSettings):
        super().__init__()
        self.settings = settings

    @provide
    def provide_settings(self) -> RatingSettings:
        return self.settings

    @provide
    @staticmethod
    async def provide_engine(
        settings: RatingSettings,
    ) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(settings)
        yield engine
        await engine.dispose()

    @provide
    @staticmethod
    def provide_session_factory(
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    @staticmethod
    async def provide_session(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @provide(scope=Scope.REQUEST)
    @staticmethod
    def provide_transaction_manager(session: AsyncSession) -> TransactionManager:
        return SQLAlchemyTransactionManager(session=session)
