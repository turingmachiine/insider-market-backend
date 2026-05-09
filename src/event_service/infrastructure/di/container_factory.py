from dishka import AsyncContainer, make_async_container

from src.event_service.core.config import EventSettings
from src.event_service.infrastructure.di.providers import (
    DatabaseProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)


def create_container(settings: EventSettings) -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(settings),
        RepositoryProvider(),
        MapperProvider(),
        UseCaseProvider(),
    )
