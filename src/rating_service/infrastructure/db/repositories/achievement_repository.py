from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rating_service.domain.entities import AchievementDefinition, UserAchievement
from src.rating_service.domain.interfaces.repositories import IAchievementRepository
from src.rating_service.infrastructure.db.tables import (
    achievement_definitions_table,
    user_achievements_table,
)


class AchievementRepository(IAchievementRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.definition_model = AchievementDefinition
        self.user_achievement_model = UserAchievement

    async def get_definitions(
        self,
        active_only: bool = True,
    ) -> list[AchievementDefinition]:
        query = select(self.definition_model).order_by(
            achievement_definitions_table.c.threshold,
            achievement_definitions_table.c.code,
        )
        if active_only:
            query = query.where(achievement_definitions_table.c.is_active.is_(True))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_definition(self, code: str) -> AchievementDefinition | None:
        query = select(self.definition_model).where(
            achievement_definitions_table.c.code == code.strip().lower()
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def save_definition(
        self,
        definition: AchievementDefinition,
    ) -> AchievementDefinition:
        self.session.add(definition)
        await self.session.flush()
        return definition

    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievement]:
        query = (
            select(self.user_achievement_model)
            .where(user_achievements_table.c.user_id == user_id)
            .order_by(user_achievements_table.c.awarded_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

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

    async def save_user_achievement(
        self,
        achievement: UserAchievement,
    ) -> UserAchievement:
        self.session.add(achievement)
        await self.session.flush()
        return achievement
