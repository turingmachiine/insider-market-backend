from dishka import AsyncContainer, make_async_container

from src.backend.auth_service.core.config import AuthSettings
from src.backend.auth_service.infrastructure.di.providers import (
    CacheProvider,
    ContainerProvider,
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
)


def create_container(settings: AuthSettings) -> AsyncContainer:
    """Создание DI контейнера auth service."""
    return make_async_container(
        ContainerProvider(settings),
        DatabaseProvider(),
        CacheProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )
