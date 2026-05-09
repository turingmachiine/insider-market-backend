from dishka import AsyncContainer, make_async_container

from src.rumor_service.core.config import RumorSettings
from src.rumor_service.infrastructure.di.providers import (
    DatabaseProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)


def create_container(settings: RumorSettings) -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(settings),
        RepositoryProvider(),
        MapperProvider(),
        UseCaseProvider(),
    )
