from dishka import Provider, Scope, provide

from src.backend.rating_service.application.mappers import RatingMapper


class MapperProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_rating_mapper() -> RatingMapper:
        return RatingMapper()
