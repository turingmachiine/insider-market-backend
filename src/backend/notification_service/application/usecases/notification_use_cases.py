from collections.abc import AsyncIterator

from src.backend.notification_service.application.dto import (
    NotificationEventDTO,
    PublishNotificationDTO,
    SubscriptionDTO,
)
from src.backend.notification_service.application.ports import INotificationBroker
from src.backend.notification_service.domain.entities import NotificationEvent
from src.backend.notification_service.domain.services import SubscriptionService


class NotificationUseCases:
    def __init__(
        self,
        broker: INotificationBroker,
        subscription_service: SubscriptionService,
    ) -> None:
        self.broker = broker
        self.subscription_service = subscription_service

    async def publish(self, dto: PublishNotificationDTO) -> NotificationEventDTO:
        event = NotificationEvent(
            topic=dto.topic,
            event_type=dto.event_type,
            payload=dto.payload,
            user_id=dto.user_id,
        )
        channels = self.subscription_service.publish_channels(event)
        await self.broker.publish(event, channels)
        return self._to_dto(event, channels)

    def build_subscription(self, dto: SubscriptionDTO) -> set[str]:
        return self.subscription_service.subscription_channels(
            topics=dto.topics,
            user_id=dto.user_id,
        )

    async def subscribe(
        self,
        dto: SubscriptionDTO,
    ) -> AsyncIterator[NotificationEvent]:
        channels = self.build_subscription(dto)
        async for event in self.broker.subscribe(channels):
            yield event

    @staticmethod
    def _to_dto(
        event: NotificationEvent,
        channels: set[str],
    ) -> NotificationEventDTO:
        return NotificationEventDTO(
            id=event.id,
            topic=event.topic,
            event_type=event.event_type,
            payload=event.payload,
            user_id=event.user_id,
            created_at=event.created_at,
            channels=channels,
        )
