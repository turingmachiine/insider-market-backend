from src.profile_service.infrastructure.db.repositories import (
    achievement_repository,
    activity_repository,
    balance_repository,
    profile_repository,
)

AchievementRepository = achievement_repository.AchievementRepository
ActivityRepository = activity_repository.ActivityRepository
BalanceRepository = balance_repository.BalanceRepository
ProfileRepository = profile_repository.ProfileRepository

__all__ = [
    "AchievementRepository",
    "ActivityRepository",
    "BalanceRepository",
    "ProfileRepository",
]
