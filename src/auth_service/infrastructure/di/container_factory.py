from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.auth_service.core.config import AuthSettings
from src.auth_service.infrastructure.di.providers import (
    ClientProvider,
    ContainerProvider,
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
)
from src.common.infrastructure.di import FastAPIRequestContextDIProvider


def create_container(settings: AuthSettings) -> AsyncContainer:
    """Создание DI контейнера auth service."""
    return make_async_container(
        ContainerProvider(settings),
        DatabaseProvider(),
        FastapiProvider(),
        FastAPIRequestContextDIProvider(),
        ClientProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )
