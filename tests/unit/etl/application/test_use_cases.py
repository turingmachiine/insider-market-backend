from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.etl_service.application.dto import (
    CreateRawPublicationDTO,
    CreateRumorDTO,
    RawPublicationDTO,
    RumorDTO,
    SourceDTO,
)
from src.etl_service.application.usecases import (
    ImportRawPublicationsUseCase,
    NormalizeRumorsUseCase,
)
from src.etl_service.domain.entities import (
    ExternalPublication,
    NormalizedRumorCandidate,
)


class FakeRumorService:
    def __init__(
        self,
        *,
        sources: list[SourceDTO],
        raw_publications: list[RawPublicationDTO] | None = None,
        rumors: list[RumorDTO] | None = None,
    ) -> None:
        self.sources = sources
        self.raw_publications = raw_publications or []
        self.rumors = rumors or []
        self.created_raw_publications: list[CreateRawPublicationDTO] = []
        self.created_rumors: list[CreateRumorDTO] = []

    async def get_active_sources(self) -> list[SourceDTO]:
        return self.sources

    async def get_raw_publications_by_source(
        self,
        source_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[RawPublicationDTO]:
        return [item for item in self.raw_publications if item.source_id == source_id][
            offset : offset + limit
        ]

    async def create_raw_publication(
        self,
        dto: CreateRawPublicationDTO,
    ) -> RawPublicationDTO:
        self.created_raw_publications.append(dto)
        publication = RawPublicationDTO(
            id=uuid4(),
            source_id=dto.source_id,
            text=dto.text,
            external_id=dto.external_id,
            url=dto.url,
            published_at=dto.published_at,
            collected_at=now(),
            payload=dto.payload,
        )
        self.raw_publications.append(publication)
        return publication

    async def get_rumors_by_source(
        self,
        source_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[RumorDTO]:
        return [item for item in self.rumors if item.source_id == source_id][
            offset : offset + limit
        ]

    async def create_rumor(self, dto: CreateRumorDTO) -> RumorDTO:
        self.created_rumors.append(dto)
        rumor = RumorDTO(
            id=uuid4(),
            source_id=dto.source_id,
            title=dto.title,
            text=dto.text,
            normalized_text=dto.normalized_text,
            raw_publication_id=dto.raw_publication_id,
            confidence_score=dto.confidence_score,
            status=dto.status,
            tags=dto.tags,
            event_candidate_payload=dto.event_candidate_payload,
            created_at=now(),
            updated_at=now(),
        )
        self.rumors.append(rumor)
        return rumor


class FakePublicationFetcher:
    def __init__(self, publications: list[ExternalPublication]) -> None:
        self.publications = publications

    async def fetch(self, source: SourceDTO) -> list[ExternalPublication]:
        return self.publications


class FakeRumorExtractor:
    def __init__(self, candidates: list[NormalizedRumorCandidate]) -> None:
        self.candidates = candidates

    def extract(
        self,
        publication: RawPublicationDTO,
        source: SourceDTO,
    ) -> list[NormalizedRumorCandidate]:
        return self.candidates


def now() -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC)


def source() -> SourceDTO:
    return SourceDTO(
        id=uuid4(),
        name="Insider",
        source_type="telegram",
        handle="@insider",
        url=None,
        weight=2.0,
        is_active=True,
        created_at=now(),
        updated_at=now(),
    )


@pytest.mark.asyncio
async def test_import_raw_publications_skips_existing_external_id() -> None:
    test_source = source()
    existing = RawPublicationDTO(
        id=uuid4(),
        source_id=test_source.id,
        text="Existing publication",
        external_id="post-1",
        url=None,
        published_at=None,
        collected_at=now(),
        payload={},
    )
    rumor_service = FakeRumorService(
        sources=[test_source],
        raw_publications=[existing],
    )
    fetcher = FakePublicationFetcher(
        [
            ExternalPublication(text="Existing publication", external_id="post-1"),
            ExternalPublication(text="New transfer rumor", external_id="post-2"),
        ]
    )

    result = await ImportRawPublicationsUseCase(
        rumor_service=rumor_service,
        publication_fetcher=fetcher,
    ).execute()

    assert result.sources_seen == 1
    assert result.publications_seen == 2
    assert result.publications_created == 1
    assert result.publications_skipped == 1
    assert rumor_service.created_raw_publications[0].external_id == "post-2"


@pytest.mark.asyncio
async def test_normalize_rumors_skips_already_processed_publication() -> None:
    test_source = source()
    processed_publication = RawPublicationDTO(
        id=uuid4(),
        source_id=test_source.id,
        text="Player already processed",
        external_id="post-1",
        url=None,
        published_at=None,
        collected_at=now(),
        payload={},
    )
    new_publication = RawPublicationDTO(
        id=uuid4(),
        source_id=test_source.id,
        text="Player will sign a contract",
        external_id="post-2",
        url=None,
        published_at=None,
        collected_at=now(),
        payload={},
    )
    existing_rumor = RumorDTO(
        id=uuid4(),
        source_id=test_source.id,
        title="Processed",
        text="Player already processed",
        normalized_text="player already processed",
        raw_publication_id=processed_publication.id,
        confidence_score=0.7,
        status="candidate",
        tags=["transfer"],
        event_candidate_payload={},
        created_at=now(),
        updated_at=now(),
    )
    candidate = NormalizedRumorCandidate(
        source_id=test_source.id,
        title="Player will sign a contract",
        text="Player will sign a contract",
        normalized_text="player will sign a contract",
        raw_publication_id=new_publication.id,
        confidence_score=0.8,
        tags=["transfer"],
    )
    rumor_service = FakeRumorService(
        sources=[test_source],
        raw_publications=[processed_publication, new_publication],
        rumors=[existing_rumor],
    )

    result = await NormalizeRumorsUseCase(
        rumor_service=rumor_service,
        rumor_extractor=FakeRumorExtractor([candidate]),
    ).execute()

    assert result.sources_seen == 1
    assert result.publications_seen == 2
    assert result.rumors_created == 1
    assert result.publications_skipped == 1
    assert rumor_service.created_rumors[0].raw_publication_id == new_publication.id
