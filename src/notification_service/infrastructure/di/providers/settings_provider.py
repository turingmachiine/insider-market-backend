from dishka import Provider, Scope, provide

from src.notification_service.core.config import NotificationSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    def __init__(self, settings: NotificationSettings) -> None:
        super().__init__()
        self.settings = settings

    @provide
    def provide_settings(self) -> NotificationSettings:
        return self.settings
