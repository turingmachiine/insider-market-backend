from dishka import AsyncContainer, make_async_container

from src.market_service.core.config import MarketSettings
from src.market_service.infrastructure.di.providers import (
    DatabaseProvider,
    DomainServiceProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)


def create_container(settings: MarketSettings) -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(settings),
        RepositoryProvider(),
        MapperProvider(),
        DomainServiceProvider(),
        UseCaseProvider(),
    )
