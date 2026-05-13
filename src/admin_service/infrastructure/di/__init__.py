from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.admin_service.core.config import AdminSettings
from src.admin_service.infrastructure.di.providers import (
    ClientProvider,
    ContainerProvider,
    DatabaseProvider,
    MapperProvider,
    RepositoryProvider,
    ServiceProvider,
)
from src.common.infrastructure.di import FastAPIRequestContextDIProvider


def create_container(settings: AdminSettings) -> AsyncContainer:
    return make_async_container(
        ContainerProvider(settings),
        DatabaseProvider(),
        FastapiProvider(),
        FastAPIRequestContextDIProvider(),
        ClientProvider(),
        RepositoryProvider(),
        MapperProvider(),
        ServiceProvider(),
    )
