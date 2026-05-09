from uuid import uuid4

from src.rumor_service.domain.entities import (
    RawPublication,
    Rumor,
    RumorStatus,
    Source,
    SourceType,
)


def test_source_defaults() -> None:
    source = Source(
        id=uuid4(),
        name="Telegram Insider",
        source_type=SourceType.TELEGRAM,
    )

    assert source.weight == 1.0
    assert source.is_active is True
    assert source.source_type == SourceType.TELEGRAM


def test_raw_publication_defaults_payload() -> None:
    publication = RawPublication(
        id=uuid4(),
        source_id=uuid4(),
        text="Coach can leave the club after the season.",
    )

    assert publication.payload == {}
    assert publication.external_id is None
    assert publication.url is None


def test_rumor_defaults_status_and_candidate_payload() -> None:
    rumor = Rumor(
        id=uuid4(),
        source_id=uuid4(),
        title="Coach exit",
        text="Coach can leave the club after the season.",
    )

    assert rumor.status == RumorStatus.NEW
    assert rumor.confidence_score == 0.0
    assert rumor.tags == []
    assert rumor.event_candidate_payload == {}
