from collections.abc import AsyncIterable

import redis.asyncio as redis
from dishka import Provider, Scope, provide

from src.notification_service.application.ports import INotificationBroker
from src.notification_service.core.config import NotificationSettings
from src.notification_service.infrastructure.pubsub import (
    InMemoryNotificationBroker,
    RedisNotificationBroker,
)


class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    async def provide_redis_client(
        settings: NotificationSettings,
    ) -> AsyncIterable[redis.Redis | None]:
        if settings.REDIS_URL is None:
            yield None
            return
        client = redis.from_url(settings.REDIS_URL)
        try:
            yield client
        finally:
            await client.aclose()

    @provide
    @staticmethod
    def provide_notification_broker(
        client: redis.Redis | None,
    ) -> INotificationBroker:
        if client is None:
            return InMemoryNotificationBroker()
        return RedisNotificationBroker(client)
