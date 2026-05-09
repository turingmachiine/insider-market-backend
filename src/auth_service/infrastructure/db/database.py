from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.auth_service.core.config import AuthSettings


def create_engine(settings: AuthSettings) -> AsyncEngine:
    return create_async_engine(
        str(settings.DATABASE_URL_AUTH),
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
