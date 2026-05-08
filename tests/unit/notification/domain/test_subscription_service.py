from uuid import uuid4

from src.backend.notification_service.domain.entities import (
    NotificationEvent,
    NotificationTopic,
)
from src.backend.notification_service.domain.services import SubscriptionService


def test_public_event_is_published_to_topic_channel() -> None:
    service = SubscriptionService("notifications")
    event = NotificationEvent(
        topic=NotificationTopic.MARKET,
        event_type="market.odds_changed",
        payload={"market_id": "m-1"},
    )

    assert service.publish_channels(event) == {"notifications.topic.market"}


def test_user_event_is_published_to_topic_and_user_channels() -> None:
    service = SubscriptionService("notifications")
    user_id = uuid4()
    event = NotificationEvent(
        topic=NotificationTopic.SYSTEM,
        event_type="system.message",
        payload={"message": "hello"},
        user_id=user_id,
    )

    assert service.publish_channels(event) == {
        "notifications.topic.system",
        f"notifications.user.{user_id}",
    }


def test_subscription_uses_topics_and_optional_user_channel() -> None:
    service = SubscriptionService("notifications")
    user_id = uuid4()

    assert service.subscription_channels(
        topics={NotificationTopic.EVENT, NotificationTopic.RATING},
        user_id=user_id,
    ) == {
        "notifications.topic.event",
        "notifications.topic.rating",
        f"notifications.user.{user_id}",
    }
