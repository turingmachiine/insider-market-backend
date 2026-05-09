from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.market_service.core.config import MarketSettings


def create_engine(settings: MarketSettings) -> AsyncEngine:
    return create_async_engine(
        str(settings.DATABASE_URL_MARKET),
        echo=settings.DEBUG,
        future=True,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
