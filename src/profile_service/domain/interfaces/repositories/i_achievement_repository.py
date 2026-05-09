from abc import ABC, abstractmethod
from uuid import UUID

from src.profile_service.domain.entities import Achievement, UserAchievement


class IAchievementRepository(ABC):
    @abstractmethod
    async def get_achievement(self, code: str) -> Achievement | None:
        pass

    @abstractmethod
    async def get_achievements(self) -> list[Achievement]:
        pass

    @abstractmethod
    async def save_achievement(self, achievement: Achievement) -> Achievement:
        pass

    @abstractmethod
    async def get_user_achievement(
        self,
        user_id: UUID,
        achievement_code: str,
    ) -> UserAchievement | None:
        pass

    @abstractmethod
    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievement]:
        pass

    @abstractmethod
    async def save_user_achievement(
        self,
        user_achievement: UserAchievement,
    ) -> UserAchievement:
        pass
