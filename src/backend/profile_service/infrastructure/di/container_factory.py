from dishka import AsyncContainer, make_async_container

from src.backend.profile_service.core.config import ProfileSettings
from src.backend.profile_service.infrastructure.di.providers import (
    DatabaseProvider,
    MapperProvider,
    RepositoryProvider,
    UseCaseProvider,
)


def create_container(settings: ProfileSettings) -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(settings),
        RepositoryProvider(),
        MapperProvider(),
        UseCaseProvider(),
    )
