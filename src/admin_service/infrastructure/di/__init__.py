from dishka import AsyncContainer, make_async_container

from src.admin_service.core.config import AdminSettings
from src.admin_service.infrastructure.di.providers import (
    ClientProvider,
    ContainerProvider,
    DatabaseProvider,
    MapperProvider,
    RepositoryProvider,
    ServiceProvider,
)


def create_container(settings: AdminSettings) -> AsyncContainer:
    return make_async_container(
        ContainerProvider(settings),
        DatabaseProvider(),
        ClientProvider(),
        RepositoryProvider(),
        MapperProvider(),
        ServiceProvider(),
    )
