from dishka import Provider, Scope, provide

from src.rumor_service.application.mappers import (
    IRawPublicationMapper,
    IRumorMapper,
    ISourceMapper,
    RawPublicationMapper,
    RumorMapper,
    SourceMapper,
)


class MapperProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_source_mapper(self) -> ISourceMapper:
        return SourceMapper()

    @provide
    def provide_raw_publication_mapper(self) -> IRawPublicationMapper:
        return RawPublicationMapper()

    @provide
    def provide_rumor_mapper(self) -> IRumorMapper:
        return RumorMapper()
