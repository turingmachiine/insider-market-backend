from src.backend.profile_service.domain.interfaces.repositories import (
    i_achievement_repository,
    i_activity_repository,
    i_balance_repository,
    i_profile_repository,
)

IAchievementRepository = i_achievement_repository.IAchievementRepository
IActivityRepository = i_activity_repository.IActivityRepository
IBalanceRepository = i_balance_repository.IBalanceRepository
IProfileRepository = i_profile_repository.IProfileRepository

__all__ = [
    "IAchievementRepository",
    "IActivityRepository",
    "IBalanceRepository",
    "IProfileRepository",
]
