from src.backend.common.application.decorators import use_case
from src.backend.etl_service.application.dto import (
    CreateRumorDTO,
    NormalizeRumorsResultDTO,
    RumorDTO,
)
from src.backend.etl_service.application.ports import RumorExtractor, RumorServicePort


@use_case
class NormalizeRumorsUseCase:
    rumor_service: RumorServicePort
    rumor_extractor: RumorExtractor
    raw_publications_limit: int = 500
    existing_rumors_limit: int = 500

    async def execute(self) -> NormalizeRumorsResultDTO:
        sources = await self.rumor_service.get_active_sources()
        publications_seen = 0
        rumors_created = 0
        publications_skipped = 0

        for source in sources:
            publications = await self.rumor_service.get_raw_publications_by_source(
                source.id,
                limit=self.raw_publications_limit,
            )
            rumors = await self.rumor_service.get_rumors_by_source(
                source.id,
                limit=self.existing_rumors_limit,
            )
            processed_publication_ids = self._build_processed_publication_ids(rumors)
            publications_seen += len(publications)

            for publication in publications:
                if publication.id in processed_publication_ids:
                    publications_skipped += 1
                    continue

                candidates = self.rumor_extractor.extract(publication, source)
                if not candidates:
                    publications_skipped += 1
                    continue

                for candidate in candidates:
                    await self.rumor_service.create_rumor(
                        CreateRumorDTO(
                            source_id=candidate.source_id,
                            title=candidate.title,
                            text=candidate.text,
                            normalized_text=candidate.normalized_text,
                            raw_publication_id=candidate.raw_publication_id,
                            confidence_score=candidate.confidence_score,
                            tags=candidate.tags,
                            event_candidate_payload=(candidate.event_candidate_payload),
                        )
                    )
                    rumors_created += 1
                processed_publication_ids.add(publication.id)

        return NormalizeRumorsResultDTO(
            sources_seen=len(sources),
            publications_seen=publications_seen,
            rumors_created=rumors_created,
            publications_skipped=publications_skipped,
        )

    @staticmethod
    def _build_processed_publication_ids(rumors: list[RumorDTO]) -> set:
        return {
            rumor.raw_publication_id
            for rumor in rumors
            if rumor.raw_publication_id is not None
        }
