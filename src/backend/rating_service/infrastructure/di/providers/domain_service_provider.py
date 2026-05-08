from dishka import Provider, Scope, provide

from src.backend.rating_service.domain.services import AchievementService


class DomainServiceProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_achievement_service() -> AchievementService:
        return AchievementService()
