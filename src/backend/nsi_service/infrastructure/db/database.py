"""База данных - конфигурация и сессии"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.backend.nsi_service.core.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Создание асинхронного движка БД"""
    db_url = str(settings.DATABASE_URL_NSI or settings.DATABASE_URL)
    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Создание фабрики сессий"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
