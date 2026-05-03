from abc import ABC, abstractmethod

from src.backend.rumor_service.application.dto import RawPublicationDTO
from src.backend.rumor_service.domain.entities import RawPublication


class IRawPublicationMapper(ABC):
    @abstractmethod
    def to_dto(self, entity: RawPublication) -> RawPublicationDTO:
        pass


class RawPublicationMapper(IRawPublicationMapper):
    def to_dto(self, entity: RawPublication) -> RawPublicationDTO:
        return RawPublicationDTO(
            id=entity.id,
            source_id=entity.source_id,
            text=entity.text,
            external_id=entity.external_id,
            url=entity.url,
            published_at=entity.published_at,
            collected_at=entity.collected_at,
            payload=entity.payload,
        )
