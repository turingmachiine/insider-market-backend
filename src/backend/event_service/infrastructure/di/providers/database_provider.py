from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.backend.common.domain.interfaces import TransactionManager
from src.backend.event_service.core.config import EventSettings
from src.backend.event_service.infrastructure.db.database import (
    create_engine,
    create_session_factory,
)
from src.backend.event_service.infrastructure.db.transaction_manager import (
    EventTransactionManager,
)


class DatabaseProvider(Provider):
    def __init__(self, settings: EventSettings):
        super().__init__()
        self.settings = settings

    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        return create_engine(self.settings)

    @provide(scope=Scope.APP)
    def provide_session_factory(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def provide_transaction_manager(
        self,
        session: AsyncSession,
    ) -> TransactionManager:
        return EventTransactionManager(session)
