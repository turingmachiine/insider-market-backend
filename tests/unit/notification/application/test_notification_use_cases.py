import asyncio
from collections.abc import AsyncGenerator
from typing import cast

from src.notification_service.application.dto import (
    PublishNotificationDTO,
    SubscriptionDTO,
)
from src.notification_service.application.usecases import NotificationUseCases
from src.notification_service.domain.entities import (
    NotificationEvent,
    NotificationTopic,
)
from src.notification_service.domain.services import SubscriptionService
from src.notification_service.infrastructure.pubsub import InMemoryNotificationBroker


async def test_publish_sends_event_to_broker() -> None:
    broker = InMemoryNotificationBroker()
    use_cases = NotificationUseCases(
        broker=broker,
        subscription_service=SubscriptionService("notifications"),
    )
    events = cast(
        AsyncGenerator[NotificationEvent, None],
        use_cases.subscribe(SubscriptionDTO(topics={NotificationTopic.MARKET})),
    )

    async def receive_next() -> NotificationEvent:
        return await anext(events)

    next_event: asyncio.Task[NotificationEvent] = asyncio.create_task(receive_next())
    await asyncio.sleep(0)

    result = await use_cases.publish(
        PublishNotificationDTO(
            topic=NotificationTopic.MARKET,
            event_type="market.odds_changed",
            payload={"market_id": "m-1"},
        )
    )

    assert result.topic == NotificationTopic.MARKET
    assert result.event_type == "market.odds_changed"
    assert result.channels == {"notifications.topic.market"}
    event = await asyncio.wait_for(next_event, timeout=1)
    assert event.id == result.id
    await events.aclose()
