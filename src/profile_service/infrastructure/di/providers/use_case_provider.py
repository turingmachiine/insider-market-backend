from dishka import Provider, Scope, provide

from src.common.domain.interfaces import TransactionManager
from src.profile_service.application.mappers import (
    IAchievementMapper,
    IActivityMapper,
    IBalanceMapper,
    IProfileMapper,
)
from src.profile_service.application.usecases import ProfileUseCases
from src.profile_service.domain.interfaces.repositories import (
    IAchievementRepository,
    IActivityRepository,
    IBalanceRepository,
    IProfileRepository,
)


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_profile_use_cases(
        profile_repository: IProfileRepository,
        balance_repository: IBalanceRepository,
        activity_repository: IActivityRepository,
        achievement_repository: IAchievementRepository,
        profile_mapper: IProfileMapper,
        balance_mapper: IBalanceMapper,
        activity_mapper: IActivityMapper,
        achievement_mapper: IAchievementMapper,
        transaction_manager: TransactionManager,
    ) -> ProfileUseCases:
        return ProfileUseCases(
            profile_repository=profile_repository,
            balance_repository=balance_repository,
            activity_repository=activity_repository,
            achievement_repository=achievement_repository,
            profile_mapper=profile_mapper,
            balance_mapper=balance_mapper,
            activity_mapper=activity_mapper,
            achievement_mapper=achievement_mapper,
            transaction_manager=transaction_manager,
        )
