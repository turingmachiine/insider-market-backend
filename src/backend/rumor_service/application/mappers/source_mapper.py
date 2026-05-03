from abc import ABC, abstractmethod

from src.backend.rumor_service.application.dto import SourceDTO
from src.backend.rumor_service.domain.entities import Source


class ISourceMapper(ABC):
    @abstractmethod
    def to_dto(self, entity: Source) -> SourceDTO:
        pass


class SourceMapper(ISourceMapper):
    def to_dto(self, entity: Source) -> SourceDTO:
        return SourceDTO(
            id=entity.id,
            name=entity.name,
            source_type=entity.source_type,
            handle=entity.handle,
            url=entity.url,
            weight=entity.weight,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
