from uuid import uuid4

import pytest

from src.event_service.domain.entities import Event, EventOutcome, EventStatus


def test_event_defaults_to_draft() -> None:
    event = Event(
        id=uuid4(),
        title="Coach exit",
        description="Coach can leave the club after the season.",
    )

    assert event.status == EventStatus.DRAFT
    assert event.candidate_payload == {}
    assert event.outcome is None


def test_event_approval_flow() -> None:
    event = Event(
        id=uuid4(),
        title="Forward transfer",
        description="Forward can move in summer.",
    )

    event.submit_for_moderation()
    event.approve()

    assert event.status == EventStatus.ACTIVE


def test_event_resolve_requires_active_status() -> None:
    event = Event(
        id=uuid4(),
        title="Forward transfer",
        description="Forward can move in summer.",
    )

    with pytest.raises(ValueError, match="Expected event status active"):
        event.resolve(EventOutcome.YES)


def test_event_resolve_sets_outcome() -> None:
    resolver_id = uuid4()
    event = Event(
        id=uuid4(),
        title="Forward transfer",
        description="Forward can move in summer.",
        status=EventStatus.ACTIVE,
    )

    event.resolve(
        outcome=EventOutcome.YES,
        resolved_by_user_id=resolver_id,
        notes="Transfer completed.",
    )

    assert event.status == EventStatus.RESOLVED
    assert event.outcome == EventOutcome.YES
    assert event.resolved_by_user_id == resolver_id
    assert event.resolved_at is not None
    assert event.resolution_notes == "Transfer completed."
