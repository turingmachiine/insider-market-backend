from dishka import Provider, Scope, provide

from src.notification_service.application.ports import INotificationBroker
from src.notification_service.application.usecases import NotificationUseCases
from src.notification_service.domain.services import SubscriptionService


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_notification_use_cases(
        broker: INotificationBroker,
        subscription_service: SubscriptionService,
    ) -> NotificationUseCases:
        return NotificationUseCases(
            broker=broker,
            subscription_service=subscription_service,
        )
