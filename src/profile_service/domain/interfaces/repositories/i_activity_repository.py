from abc import ABC, abstractmethod
from uuid import UUID

from src.profile_service.domain.entities import Activity, ActivityType


class IActivityRepository(ABC):
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        activity_type: ActivityType | None = None,
    ) -> list[Activity]:
        pass

    @abstractmethod
    async def save(self, activity: Activity) -> Activity:
        pass
