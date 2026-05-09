from abc import ABC, abstractmethod
from uuid import UUID

from src.rating_service.domain.entities import AchievementDefinition, UserAchievement


class IAchievementRepository(ABC):
    @abstractmethod
    async def get_definitions(
        self, active_only: bool = True
    ) -> list[AchievementDefinition]:
        raise NotImplementedError

    @abstractmethod
    async def get_definition(self, code: str) -> AchievementDefinition | None:
        raise NotImplementedError

    @abstractmethod
    async def save_definition(
        self,
        definition: AchievementDefinition,
    ) -> AchievementDefinition:
        raise NotImplementedError

    @abstractmethod
    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievement]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_achievement(
        self,
        user_id: UUID,
        achievement_code: str,
    ) -> UserAchievement | None:
        raise NotImplementedError

    @abstractmethod
    async def save_user_achievement(
        self,
        achievement: UserAchievement,
    ) -> UserAchievement:
        raise NotImplementedError
