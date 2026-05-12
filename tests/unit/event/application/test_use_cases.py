from uuid import UUID, uuid4

import pytest

from src.common.domain.interfaces import TransactionManager
from src.event_service.application.constants import EVENT_ACCESS_DENIED_DETAIL
from src.event_service.application.dto import (
    CreateEventDTO,
    ResolveEventDTO,
    UpdateEventDTO,
)
from src.event_service.application.mappers import EventMapper
from src.event_service.application.usecases import EventUseCases
from src.event_service.domain.entities import Event, EventOutcome, EventStatus
from src.event_service.domain.interfaces.repositories import IEventRepository


class FakeTransactionManager(TransactionManager):
    def __init__(self) -> None:
        self.begins = 0
        self.commits = 0
        self.rollbacks = 0
        self.flushes = 0
        self._in_transaction = False
        self._in_nested = False

    async def begin(self) -> None:
        self.begins += 1
        self._in_transaction = True

    async def begin_nested(self) -> None:
        self._in_nested = True

    async def commit(self) -> None:
        self.commits += 1
        self._in_transaction = False
        self._in_nested = False

    async def rollback(self) -> None:
        self.rollbacks += 1
        self._in_transaction = False
        self._in_nested = False

    async def flush(self) -> None:
        self.flushes += 1

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    @property
    def in_nested(self) -> bool:
        return self._in_nested


class FakeEventRepository(IEventRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Event] = {}

    async def get_by_id(self, event_id: UUID) -> Event | None:
        return self.items.get(event_id)

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: EventStatus | None = None,
        source_rumor_id: UUID | None = None,
    ) -> list[Event]:
        items = list(self.items.values())
        if status is not None:
            items = [item for item in items if item.status == status]
        if source_rumor_id is not None:
            items = [item for item in items if item.source_rumor_id == source_rumor_id]
        return items[offset : offset + limit]

    async def save(self, event: Event) -> Event:
        self.items[event.id] = event
        return event


@pytest.fixture
def transaction_manager() -> FakeTransactionManager:
    return FakeTransactionManager()


@pytest.fixture
def event_repository() -> FakeEventRepository:
    return FakeEventRepository()


def create_use_cases(
    event_repository: FakeEventRepository,
    transaction_manager: FakeTransactionManager,
) -> EventUseCases:
    return EventUseCases(
        event_repository=event_repository,
        event_mapper=EventMapper(),
        transaction_manager=transaction_manager,
    )


@pytest.mark.asyncio
async def test_create_event_can_submit_to_moderation(
    event_repository: FakeEventRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    use_cases = create_use_cases(event_repository, transaction_manager)

    result = await use_cases.create_event(
        CreateEventDTO(
            title="Coach exit",
            description="Coach can leave the club.",
            submit_for_moderation=True,
        )
    )

    assert result.status == EventStatus.PENDING_MODERATION
    assert result.id in event_repository.items
    assert transaction_manager.commits == 1
    assert transaction_manager.rollbacks == 0


@pytest.mark.asyncio
async def test_moderation_queue_returns_pending_events(
    event_repository: FakeEventRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    pending = Event(
        id=uuid4(),
        title="Pending",
        description="Pending event.",
        status=EventStatus.PENDING_MODERATION,
    )
    active = Event(
        id=uuid4(),
        title="Active",
        description="Active event.",
        status=EventStatus.ACTIVE,
    )
    await event_repository.save(pending)
    await event_repository.save(active)
    use_cases = create_use_cases(event_repository, transaction_manager)

    result = await use_cases.get_moderation_queue()

    assert [item.id for item in result] == [pending.id]


@pytest.mark.asyncio
async def test_approve_and_resolve_event(
    event_repository: FakeEventRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    event = Event(
        id=uuid4(),
        title="Forward transfer",
        description="Forward can move.",
        status=EventStatus.PENDING_MODERATION,
    )
    await event_repository.save(event)
    use_cases = create_use_cases(event_repository, transaction_manager)

    approved = await use_cases.approve_event(event.id)
    resolved = await use_cases.resolve_event(
        event.id,
        ResolveEventDTO(outcome=EventOutcome.YES, notes="Transfer completed."),
    )

    assert approved is not None
    assert approved.status == EventStatus.ACTIVE
    assert resolved is not None
    assert resolved.status == EventStatus.RESOLVED
    assert resolved.outcome == EventOutcome.YES


@pytest.mark.asyncio
async def test_invalid_transition_rolls_back(
    event_repository: FakeEventRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    event = Event(
        id=uuid4(),
        title="Draft",
        description="Draft event.",
    )
    await event_repository.save(event)
    use_cases = create_use_cases(event_repository, transaction_manager)

    with pytest.raises(ValueError, match="Expected event status pending_moderation"):
        await use_cases.approve_event(event.id)

    assert transaction_manager.rollbacks == 1


@pytest.mark.asyncio
async def test_update_event_rejects_non_owner(
    event_repository: FakeEventRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    owner_id = uuid4()
    event = Event(
        id=uuid4(),
        title="Owner event",
        description="Draft event.",
        created_by_user_id=owner_id,
    )
    await event_repository.save(event)
    use_cases = create_use_cases(event_repository, transaction_manager)

    with pytest.raises(PermissionError, match=EVENT_ACCESS_DENIED_DETAIL):
        await use_cases.update_event(
            event.id,
            dto=UpdateEventDTO(
                title="Updated",
                description="Updated event.",
            ),
            owner_user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_submit_for_moderation_rejects_non_owner(
    event_repository: FakeEventRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    owner_id = uuid4()
    event = Event(
        id=uuid4(),
        title="Owner event",
        description="Draft event.",
        created_by_user_id=owner_id,
    )
    await event_repository.save(event)
    use_cases = create_use_cases(event_repository, transaction_manager)

    with pytest.raises(PermissionError, match=EVENT_ACCESS_DENIED_DETAIL):
        await use_cases.submit_for_moderation(
            event.id,
            owner_user_id=uuid4(),
        )
