from dishka import Provider, Scope, provide

from src.backend.auth_service.core.config import AuthSettings


class ContainerProvider(Provider):
    """Основной провайдер auth service."""

    scope = Scope.APP

    def __init__(self, settings: AuthSettings) -> None:
        super().__init__()
        self.settings = settings

    @provide
    def provide_settings(self) -> AuthSettings:
        return self.settings
