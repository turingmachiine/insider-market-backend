from abc import ABC, abstractmethod

from src.backend.profile_service.application.dto import (
    AchievementDTO,
    UserAchievementDTO,
)
from src.backend.profile_service.domain.entities import Achievement, UserAchievement


class IAchievementMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(entity: Achievement) -> AchievementDTO:
        pass

    @staticmethod
    @abstractmethod
    def user_to_dto(
        entity: UserAchievement,
        achievement: Achievement | None = None,
    ) -> UserAchievementDTO:
        pass


class AchievementMapper(IAchievementMapper):
    @staticmethod
    def to_dto(entity: Achievement) -> AchievementDTO:
        return AchievementDTO(
            code=entity.code,
            name=entity.name,
            description=entity.description,
            icon_url=entity.icon_url,
            created_at=entity.created_at,
        )

    @staticmethod
    def user_to_dto(
        entity: UserAchievement,
        achievement: Achievement | None = None,
    ) -> UserAchievementDTO:
        return UserAchievementDTO(
            id=entity.id,
            user_id=entity.user_id,
            achievement_code=entity.achievement_code,
            progress=entity.progress,
            awarded_at=entity.awarded_at,
            achievement=(
                AchievementMapper.to_dto(achievement)
                if achievement is not None
                else None
            ),
        )
