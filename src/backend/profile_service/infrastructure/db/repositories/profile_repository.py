from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.profile_service.domain.entities import Profile
from src.backend.profile_service.domain.interfaces.repositories import (
    IProfileRepository,
)
from src.backend.profile_service.infrastructure.db.tables import profiles_table


class ProfileRepository(IProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Profile

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        query = select(self.model).where(profiles_table.c.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Profile]:
        query = (
            select(self.model)
            .order_by(profiles_table.c.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, profile: Profile) -> Profile:
        self.session.add(profile)
        await self.session.flush()
        return profile
