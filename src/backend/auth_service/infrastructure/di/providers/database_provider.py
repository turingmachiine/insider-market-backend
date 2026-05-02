from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.backend.auth_service.core.config import AuthSettings
from src.backend.auth_service.infrastructure.db.database import (
    create_engine,
    create_session_factory,
)


class DatabaseProvider(Provider):
    """Провайдер зависимостей базы данных auth service."""

    scope = Scope.APP

    @provide
    async def provide_engine(
        self,
        settings: AuthSettings,
    ) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(settings)
        yield engine
        await engine.dispose()

    @provide
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
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
