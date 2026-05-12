from dishka import Provider, Scope, provide

from src.common.application.protocols import IUserProvider
from src.common.infrastructure.integration import JwtUserProvider
from src.notification_service.core.config import NotificationSettings


class IntegrationProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_user_provider(settings: NotificationSettings) -> IUserProvider:
        return JwtUserProvider(settings)
