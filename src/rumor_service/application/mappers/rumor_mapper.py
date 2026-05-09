from abc import ABC, abstractmethod

from src.rumor_service.application.dto import RumorDTO
from src.rumor_service.domain.entities import Rumor


class IRumorMapper(ABC):
    @abstractmethod
    def to_dto(self, entity: Rumor) -> RumorDTO:
        pass


class RumorMapper(IRumorMapper):
    def to_dto(self, entity: Rumor) -> RumorDTO:
        return RumorDTO(
            id=entity.id,
            source_id=entity.source_id,
            title=entity.title,
            text=entity.text,
            normalized_text=entity.normalized_text,
            raw_publication_id=entity.raw_publication_id,
            confidence_score=entity.confidence_score,
            status=entity.status,
            tags=entity.tags,
            event_candidate_payload=entity.event_candidate_payload,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
