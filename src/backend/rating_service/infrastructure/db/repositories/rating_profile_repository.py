from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.rating_service.domain.entities import RatingProfile
from src.backend.rating_service.domain.interfaces.repositories import (
    IRatingProfileRepository,
)
from src.backend.rating_service.infrastructure.db.tables import rating_profiles_table


class RatingProfileRepository(IRatingProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = RatingProfile

    async def get_by_user_id(self, user_id: UUID) -> RatingProfile | None:
        query = select(self.model).where(rating_profiles_table.c.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[RatingProfile]:
        query = (
            select(self.model)
            .order_by(rating_profiles_table.c.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        query = select(func.count()).select_from(rating_profiles_table)
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def get_leaderboard(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RatingProfile]:
        query = (
            select(self.model)
            .order_by(
                rating_profiles_table.c.rating.desc(),
                rating_profiles_table.c.xp.desc(),
                rating_profiles_table.c.updated_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, profile: RatingProfile) -> RatingProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile
