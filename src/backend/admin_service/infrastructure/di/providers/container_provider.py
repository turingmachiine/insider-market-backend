from dishka import Provider, Scope, provide

from src.backend.admin_service.core.config import AdminSettings


class ContainerProvider(Provider):
    scope = Scope.APP

    def __init__(self, settings: AdminSettings) -> None:
        super().__init__()
        self.settings = settings

    @provide
    def provide_settings(self) -> AdminSettings:
        return self.settings
