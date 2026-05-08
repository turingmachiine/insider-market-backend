from uuid import UUID

from src.backend.notification_service.domain.entities import (
    NotificationEvent,
    NotificationTopic,
)


class SubscriptionService:
    def __init__(self, channel_prefix: str) -> None:
        self.channel_prefix = channel_prefix.strip(".")

    def publish_channels(self, event: NotificationEvent) -> set[str]:
        channels = {self.topic_channel(event.topic)}
        if event.user_id is not None:
            channels.add(self.user_channel(event.user_id))
        return channels

    def subscription_channels(
        self,
        topics: set[NotificationTopic],
        user_id: UUID | None = None,
    ) -> set[str]:
        channels = {self.topic_channel(topic) for topic in topics}
        if user_id is not None:
            channels.add(self.user_channel(user_id))
        return channels

    def topic_channel(self, topic: NotificationTopic) -> str:
        return f"{self.channel_prefix}.topic.{topic.value}"

    def user_channel(self, user_id: UUID) -> str:
        return f"{self.channel_prefix}.user.{user_id}"
