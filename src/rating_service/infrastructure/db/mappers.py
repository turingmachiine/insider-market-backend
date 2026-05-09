from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

from src.rating_service.domain.entities import (
    AchievementDefinition,
    RatingEvent,
    RatingProfile,
    RewardTransaction,
    UserAchievement,
)
from src.rating_service.infrastructure.db.metadata import mapper_registry
from src.rating_service.infrastructure.db.tables import (
    achievement_definitions_table,
    rating_events_table,
    rating_profiles_table,
    reward_transactions_table,
    user_achievements_table,
)


def setup_mapping() -> None:
    try:
        inspect(RatingProfile)
        return
    except NoInspectionAvailable:
        pass

    mapper_registry.map_imperatively(RatingProfile, rating_profiles_table)
    mapper_registry.map_imperatively(RatingEvent, rating_events_table)
    mapper_registry.map_imperatively(
        AchievementDefinition,
        achievement_definitions_table,
    )
    mapper_registry.map_imperatively(UserAchievement, user_achievements_table)
    mapper_registry.map_imperatively(RewardTransaction, reward_transactions_table)


__all__ = ["setup_mapping"]
