from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from src.backend.notification_service.domain.entities import NotificationEvent


class INotificationBroker(ABC):
    @abstractmethod
    async def publish(self, event: NotificationEvent, channels: set[str]) -> None:
        pass

    @abstractmethod
    def subscribe(self, channels: set[str]) -> AsyncIterator[NotificationEvent]:
        pass
