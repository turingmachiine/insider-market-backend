from dishka import Provider, Scope, provide

from src.etl_service.core.config import ETLSettings


class ContainerProvider(Provider):
    scope = Scope.APP

    def __init__(self, settings: ETLSettings) -> None:
        super().__init__()
        self._settings = settings

    @provide
    def provide_settings(self) -> ETLSettings:
        return self._settings
