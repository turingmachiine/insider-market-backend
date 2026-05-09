from dishka import Provider, Scope, provide

from src.event_service.application.mappers import EventMapper, IEventMapper


class MapperProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_event_mapper(self) -> IEventMapper:
        return EventMapper()
