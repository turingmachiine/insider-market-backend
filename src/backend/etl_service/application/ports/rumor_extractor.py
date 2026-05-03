from typing import Protocol

from src.backend.etl_service.application.dto import RawPublicationDTO, SourceDTO
from src.backend.etl_service.domain.entities import NormalizedRumorCandidate


class RumorExtractor(Protocol):
    def extract(
        self,
        publication: RawPublicationDTO,
        source: SourceDTO,
    ) -> list[NormalizedRumorCandidate]:
        raise NotImplementedError
