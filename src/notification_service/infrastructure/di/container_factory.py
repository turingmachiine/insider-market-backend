from dishka import AsyncContainer, make_async_container

from src.notification_service.core.config import NotificationSettings
from src.notification_service.infrastructure.di.providers import (
    BrokerProvider,
    DomainServiceProvider,
    IntegrationProvider,
    SettingsProvider,
    UseCaseProvider,
)


def create_container(settings: NotificationSettings) -> AsyncContainer:
    return make_async_container(
        SettingsProvider(settings),
        IntegrationProvider(),
        BrokerProvider(),
        DomainServiceProvider(),
        UseCaseProvider(),
    )
