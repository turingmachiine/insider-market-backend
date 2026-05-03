from abc import ABC, abstractmethod

from src.backend.event_service.application.dto import EventDTO
from src.backend.event_service.domain.entities import Event


class IEventMapper(ABC):
    @abstractmethod
    def to_dto(self, entity: Event) -> EventDTO:
        pass


class EventMapper(IEventMapper):
    def to_dto(self, entity: Event) -> EventDTO:
        return EventDTO(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            status=entity.status,
            source_rumor_id=entity.source_rumor_id,
            candidate_payload=entity.candidate_payload,
            deadline_at=entity.deadline_at,
            resolution_rules=entity.resolution_rules,
            outcome=entity.outcome,
            resolution_notes=entity.resolution_notes,
            created_by_user_id=entity.created_by_user_id,
            resolved_by_user_id=entity.resolved_by_user_id,
            resolved_at=entity.resolved_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
