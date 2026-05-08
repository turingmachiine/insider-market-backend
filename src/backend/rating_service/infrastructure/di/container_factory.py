from dishka import AsyncContainer, make_async_container
from dishka.integrations.taskiq import TaskiqProvider

from src.backend.rating_service.core.config import RatingSettings
from src.backend.rating_service.infrastructure.di.providers import (
    ClientProvider,
    DatabaseProvider,
    DomainServiceProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)


def create_container(
    settings: RatingSettings,
    include_taskiq: bool = False,
) -> AsyncContainer:
    providers = [
        DatabaseProvider(settings),
        ClientProvider(),
        RepositoryProvider(),
        DomainServiceProvider(),
        MapperProvider(),
        UseCaseProvider(),
    ]
    if include_taskiq:
        providers.append(TaskiqProvider())
    return make_async_container(*providers)
