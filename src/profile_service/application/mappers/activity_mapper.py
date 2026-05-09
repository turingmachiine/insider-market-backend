from abc import ABC, abstractmethod

from src.profile_service.application.dto import ActivityDTO
from src.profile_service.domain.entities import Activity


class IActivityMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(entity: Activity) -> ActivityDTO:
        pass


class ActivityMapper(IActivityMapper):
    @staticmethod
    def to_dto(entity: Activity) -> ActivityDTO:
        return ActivityDTO(
            id=entity.id,
            user_id=entity.user_id,
            activity_type=entity.activity_type,
            title=entity.title,
            description=entity.description,
            payload=entity.payload,
            created_at=entity.created_at,
        )
