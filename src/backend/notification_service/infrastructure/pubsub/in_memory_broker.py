import asyncio
from collections.abc import AsyncIterator

from src.backend.notification_service.application.ports import INotificationBroker
from src.backend.notification_service.domain.entities import NotificationEvent


class InMemoryNotificationBroker(INotificationBroker):
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[NotificationEvent]]] = {}

    async def publish(self, event: NotificationEvent, channels: set[str]) -> None:
        for channel in channels:
            for queue in self._subscribers.get(channel, set()):
                await queue.put(event)

    async def subscribe(self, channels: set[str]) -> AsyncIterator[NotificationEvent]:
        queue: asyncio.Queue[NotificationEvent] = asyncio.Queue()
        for channel in channels:
            self._subscribers.setdefault(channel, set()).add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            for channel in channels:
                subscribers = self._subscribers.get(channel)
                if subscribers is None:
                    continue
                subscribers.discard(queue)
                if not subscribers:
                    self._subscribers.pop(channel, None)
