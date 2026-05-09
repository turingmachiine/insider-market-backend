from datetime import UTC, datetime
from uuid import UUID

from src.common.application.decorators import use_case
from src.etl_service.application.dto import (
    CreateRawPublicationDTO,
    ImportRawPublicationsResultDTO,
    RawPublicationDTO,
)
from src.etl_service.application.ports import PublicationFetcher, RumorServicePort
from src.etl_service.domain.entities import ExternalPublication

type _PublicationKeySource = RawPublicationDTO | ExternalPublication


@use_case
class ImportRawPublicationsUseCase:
    rumor_service: RumorServicePort
    publication_fetcher: PublicationFetcher
    existing_publications_limit: int = 500

    async def execute(self) -> ImportRawPublicationsResultDTO:
        sources = await self.rumor_service.get_active_sources()
        publications_seen = 0
        publications_created = 0
        publications_skipped = 0

        for source in sources:
            existing = await self.rumor_service.get_raw_publications_by_source(
                source.id,
                limit=self.existing_publications_limit,
            )
            existing_keys = self._build_existing_keys(existing)
            publications = await self.publication_fetcher.fetch(source)
            publications_seen += len(publications)

            for publication in publications:
                publication_key = self._publication_key(publication)
                if publication_key in existing_keys:
                    publications_skipped += 1
                    continue

                await self.rumor_service.create_raw_publication(
                    self._to_create_dto(source.id, publication)
                )
                existing_keys.add(publication_key)
                publications_created += 1

        return ImportRawPublicationsResultDTO(
            sources_seen=len(sources),
            publications_seen=publications_seen,
            publications_created=publications_created,
            publications_skipped=publications_skipped,
        )

    @staticmethod
    def _build_existing_keys(publications: list[RawPublicationDTO]) -> set[str]:
        return {
            ImportRawPublicationsUseCase._publication_key(publication)
            for publication in publications
        }

    @staticmethod
    def _publication_key(publication: _PublicationKeySource) -> str:
        if publication.external_id:
            return f"external:{publication.external_id}"
        if publication.url:
            return f"url:{publication.url}"
        return f"text:{publication.text.strip()}"

    @staticmethod
    def _to_create_dto(
        source_id: UUID,
        publication: ExternalPublication,
    ) -> CreateRawPublicationDTO:
        payload = {
            **publication.payload,
            "etl_collected_at": datetime.now(UTC).isoformat(),
        }
        return CreateRawPublicationDTO(
            source_id=source_id,
            text=publication.text,
            external_id=publication.external_id,
            url=publication.url,
            published_at=publication.published_at,
            payload=payload,
        )
