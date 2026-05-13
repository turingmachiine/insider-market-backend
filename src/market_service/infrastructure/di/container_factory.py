from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.common.infrastructure.di import FastAPIRequestContextDIProvider
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
        FastapiProvider(),
        FastAPIRequestContextDIProvider(),
        RepositoryProvider(),
        MapperProvider(),
        DomainServiceProvider(),
        UseCaseProvider(),
    )
