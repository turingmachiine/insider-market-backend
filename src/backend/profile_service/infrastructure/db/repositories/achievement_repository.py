from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.profile_service.domain.entities import Achievement, UserAchievement
from src.backend.profile_service.domain.interfaces.repositories import (
    IAchievementRepository,
)
from src.backend.profile_service.infrastructure.db.tables import (
    achievements_table,
    user_achievements_table,
)


class AchievementRepository(IAchievementRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.achievement_model = Achievement
        self.user_achievement_model = UserAchievement

    async def get_achievement(self, code: str) -> Achievement | None:
        query = select(self.achievement_model).where(
            achievements_table.c.code == code.strip().lower()
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_achievements(self) -> list[Achievement]:
        query = select(self.achievement_model).order_by(achievements_table.c.code)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save_achievement(self, achievement: Achievement) -> Achievement:
        self.session.add(achievement)
        await self.session.flush()
        return achievement

    async def get_user_achievement(
        self,
        user_id: UUID,
        achievement_code: str,
    ) -> UserAchievement | None:
        query = select(self.user_achievement_model).where(
            user_achievements_table.c.user_id == user_id,
            user_achievements_table.c.achievement_code
            == achievement_code.strip().lower(),
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievement]:
        query = (
            select(self.user_achievement_model)
            .where(user_achievements_table.c.user_id == user_id)
            .order_by(user_achievements_table.c.awarded_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save_user_achievement(
        self,
        user_achievement: UserAchievement,
    ) -> UserAchievement:
        self.session.add(user_achievement)
        await self.session.flush()
        return user_achievement
