from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

from src.backend.profile_service.domain.entities import (
    Achievement,
    Activity,
    BalanceTransaction,
    Profile,
    UserAchievement,
    UserBalance,
)
from src.backend.profile_service.infrastructure.db.metadata import mapper_registry
from src.backend.profile_service.infrastructure.db.tables import (
    achievements_table,
    activities_table,
    balance_transactions_table,
    profiles_table,
    user_achievements_table,
    user_balances_table,
)


def setup_mapping() -> None:
    try:
        inspect(Profile)
        return
    except NoInspectionAvailable:
        pass

    mapper_registry.map_imperatively(Profile, profiles_table)
    mapper_registry.map_imperatively(UserBalance, user_balances_table)
    mapper_registry.map_imperatively(BalanceTransaction, balance_transactions_table)
    mapper_registry.map_imperatively(Activity, activities_table)
    mapper_registry.map_imperatively(Achievement, achievements_table)
    mapper_registry.map_imperatively(UserAchievement, user_achievements_table)


__all__ = ["setup_mapping"]
