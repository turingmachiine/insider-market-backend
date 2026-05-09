from dishka import AsyncContainer, make_async_container
from dishka.integrations.taskiq import TaskiqProvider

from src.etl_service.core.config import ETLSettings
from src.etl_service.infrastructure.di.providers import (
    ContainerProvider,
    HttpClientProvider,
    PortProvider,
    UseCaseProvider,
)


def create_container(settings: ETLSettings) -> AsyncContainer:
    return make_async_container(
        ContainerProvider(settings),
        HttpClientProvider(),
        PortProvider(),
        UseCaseProvider(),
        TaskiqProvider(),
    )
