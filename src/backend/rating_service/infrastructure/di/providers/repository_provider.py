from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.rating_service.domain.interfaces.repositories import (
    IAchievementRepository,
    IRatingEventRepository,
    IRatingProfileRepository,
    IRewardRepository,
)
from src.backend.rating_service.infrastructure.db.repositories import (
    AchievementRepository,
    RatingEventRepository,
    RatingProfileRepository,
    RewardRepository,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_profile_repository(session: AsyncSession) -> IRatingProfileRepository:
        return RatingProfileRepository(session)

    @provide
    @staticmethod
    def provide_event_repository(session: AsyncSession) -> IRatingEventRepository:
        return RatingEventRepository(session)

    @provide
    @staticmethod
    def provide_achievement_repository(session: AsyncSession) -> IAchievementRepository:
        return AchievementRepository(session)

    @provide
    @staticmethod
    def provide_reward_repository(session: AsyncSession) -> IRewardRepository:
        return RewardRepository(session)
