from dishka import AsyncContainer, make_async_container

from src.core.config import Settings
from src.infrastructure.di.providers import (
    ContainerProvider,
    DatabaseProvider,
    DomainServiceProvider,
    MapperProvider,
    ProcessingProvider,
    RepositoryProvider,
    UseCaseProvider,
)


def create_container(settings: Settings) -> AsyncContainer:
    """Создание DI контейнера"""
    return make_async_container(
        ContainerProvider(settings),
        DatabaseProvider(settings),
        RepositoryProvider(),
        DomainServiceProvider(),
        MapperProvider(),
        ProcessingProvider(),
        UseCaseProvider(),
    )
