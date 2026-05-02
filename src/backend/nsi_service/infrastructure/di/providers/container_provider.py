from dishka import Provider, Scope, provide

from src.backend.nsi_service.core.config import Settings


class ContainerProvider(Provider):
    """Основной провайдер приложения"""

    scope = Scope.APP

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

    @provide
    def provide_settings(self) -> Settings:
        return self.settings
