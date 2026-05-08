from dishka import Provider, Scope, provide

from src.backend.rating_service.application.usecases import RatingUseCases


class UseCaseProvider(Provider):
    scope = Scope.REQUEST
    rating_use_cases = provide(RatingUseCases)
