import json
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any
from uuid import UUID

import redis.asyncio as redis

from src.notification_service.application.ports import INotificationBroker
from src.notification_service.domain.entities import (
    NotificationEvent,
    NotificationTopic,
)


class RedisNotificationBroker(INotificationBroker):
    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    async def publish(self, event: NotificationEvent, channels: set[str]) -> None:
        payload = self._encode(event)
        for channel in channels:
            await self.client.publish(channel, payload)

    async def subscribe(self, channels: set[str]) -> AsyncIterator[NotificationEvent]:
        pubsub = self.client.pubsub()
        await pubsub.subscribe(*channels)
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                yield self._decode(message["data"])
        finally:
            await pubsub.unsubscribe(*channels)
            await pubsub.aclose()

    @staticmethod
    def _encode(event: NotificationEvent) -> str:
        return json.dumps(
            {
                "id": str(event.id),
                "topic": event.topic.value,
                "event_type": event.event_type,
                "payload": event.payload,
                "user_id": str(event.user_id) if event.user_id else None,
                "created_at": event.created_at.isoformat(),
            },
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _decode(raw: bytes | str) -> NotificationEvent:
        data: dict[str, Any] = json.loads(
            raw.decode("utf-8") if isinstance(raw, bytes) else raw
        )
        user_id = data.get("user_id")
        return NotificationEvent(
            id=UUID(data["id"]),
            topic=NotificationTopic(data["topic"]),
            event_type=data["event_type"],
            payload=data["payload"],
            user_id=UUID(user_id) if user_id else None,
            created_at=datetime.fromisoformat(data["created_at"]),
        )
