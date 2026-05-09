from datetime import UTC, datetime
from uuid import uuid4

from src.etl_service.application.dto import RawPublicationDTO, SourceDTO
from src.etl_service.infrastructure.extractors import RuleBasedRumorExtractor


def test_rule_based_extractor_builds_transfer_candidate() -> None:
    source_id = uuid4()
    publication = RawPublicationDTO(
        id=uuid4(),
        source_id=source_id,
        text="Игрок подпишет контракт с новым клубом уже завтра.",
        external_id="post-1",
        url=None,
        published_at=None,
        collected_at=datetime(2026, 1, 1, tzinfo=UTC),
        payload={},
    )
    source = SourceDTO(
        id=source_id,
        name="Insider",
        source_type="telegram",
        handle="@insider",
        url=None,
        weight=3.0,
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    candidates = RuleBasedRumorExtractor().extract(publication, source)

    assert len(candidates) == 1
    assert candidates[0].source_id == source_id
    assert candidates[0].raw_publication_id == publication.id
    assert candidates[0].tags == ["transfer"]
    assert candidates[0].confidence_score > 0.0


def test_rule_based_extractor_ignores_non_rumor_text() -> None:
    source_id = uuid4()
    publication = RawPublicationDTO(
        id=uuid4(),
        source_id=source_id,
        text="Команда провела открытую тренировку.",
        external_id="post-1",
        url=None,
        published_at=None,
        collected_at=datetime(2026, 1, 1, tzinfo=UTC),
        payload={},
    )
    source = SourceDTO(
        id=source_id,
        name="Media",
        source_type="media",
        handle=None,
        url="https://example.com/feed",
        weight=1.0,
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert RuleBasedRumorExtractor().extract(publication, source) == []
