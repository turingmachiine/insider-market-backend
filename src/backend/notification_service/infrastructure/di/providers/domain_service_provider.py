from dishka import Provider, Scope, provide

from src.backend.notification_service.core.config import NotificationSettings
from src.backend.notification_service.domain.services import SubscriptionService


class DomainServiceProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_subscription_service(
        settings: NotificationSettings,
    ) -> SubscriptionService:
        return SubscriptionService(settings.NOTIFICATION_CHANNEL_PREFIX)
