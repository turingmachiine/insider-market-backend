from dishka import Provider, Scope, provide

from src.backend.admin_service.application.mappers import AdminMapper


class MapperProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_admin_mapper() -> AdminMapper:
        return AdminMapper()
