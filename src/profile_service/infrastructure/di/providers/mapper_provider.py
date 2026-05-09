from dishka import Provider, Scope, provide

from src.profile_service.application.mappers import (
    AchievementMapper,
    ActivityMapper,
    BalanceMapper,
    IAchievementMapper,
    IActivityMapper,
    IBalanceMapper,
    IProfileMapper,
    ProfileMapper,
)


class MapperProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_profile_mapper() -> IProfileMapper:
        return ProfileMapper()

    @provide
    @staticmethod
    def provide_balance_mapper() -> IBalanceMapper:
        return BalanceMapper()

    @provide
    @staticmethod
    def provide_activity_mapper() -> IActivityMapper:
        return ActivityMapper()

    @provide
    @staticmethod
    def provide_achievement_mapper() -> IAchievementMapper:
        return AchievementMapper()
