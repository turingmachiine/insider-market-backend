from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile_service.domain.interfaces.repositories import (
    IAchievementRepository,
    IActivityRepository,
    IBalanceRepository,
    IProfileRepository,
)
from src.profile_service.infrastructure.db.repositories import (
    AchievementRepository,
    ActivityRepository,
    BalanceRepository,
    ProfileRepository,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_profile_repository(session: AsyncSession) -> IProfileRepository:
        return ProfileRepository(session)

    @provide
    @staticmethod
    def provide_balance_repository(session: AsyncSession) -> IBalanceRepository:
        return BalanceRepository(session)

    @provide
    @staticmethod
    def provide_activity_repository(session: AsyncSession) -> IActivityRepository:
        return ActivityRepository(session)

    @provide
    @staticmethod
    def provide_achievement_repository(
        session: AsyncSession,
    ) -> IAchievementRepository:
        return AchievementRepository(session)
