from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile_service.domain.entities import Activity, ActivityType
from src.profile_service.domain.interfaces.repositories import IActivityRepository
from src.profile_service.infrastructure.db.tables import activities_table


class ActivityRepository(IActivityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Activity

    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        activity_type: ActivityType | None = None,
    ) -> list[Activity]:
        query = select(self.model).where(activities_table.c.user_id == user_id)
        if activity_type is not None:
            query = query.where(activities_table.c.activity_type == activity_type)
        query = (
            query.order_by(activities_table.c.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save(self, activity: Activity) -> Activity:
        self.session.add(activity)
        await self.session.flush()
        return activity
