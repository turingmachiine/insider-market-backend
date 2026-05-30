from uuid import UUID, uuid4

import pytest

from src.common.domain.interfaces import TransactionManager
from src.rumor_service.application.dto import (
    CreateRawPublicationDTO,
    CreateRumorDTO,
    CreateSourceDTO,
    UpdateRumorStatusDTO,
)
from src.rumor_service.application.mappers import (
    RawPublicationMapper,
    RumorMapper,
    SourceMapper,
)
from src.rumor_service.application.usecases import (
    RawPublicationUseCases,
    RumorUseCases,
    SourceUseCases,
)
from src.rumor_service.domain.entities import (
    RawPublication,
    Rumor,
    RumorStatus,
    Source,
    SourceType,
)
from src.rumor_service.domain.interfaces.repositories import (
    IRawPublicationRepository,
    IRumorRepository,
    ISourceRepository,
)


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


class FakeSourceRepository(ISourceRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Source] = {}

    async def get_by_id(self, source_id: UUID) -> Source | None:
        return self.items.get(source_id)

    async def get_by_name(self, name: str) -> Source | None:
        return next((item for item in self.items.values() if item.name == name), None)

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
    ) -> list[Source]:
        items = list(self.items.values())
        if active_only:
            items = [item for item in items if item.is_active]
        return items[offset : offset + limit]

    async def save(self, source: Source) -> Source:
        self.items[source.id] = source
        return source


class FakeRawPublicationRepository(IRawPublicationRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, RawPublication] = {}

    async def get_by_id(self, publication_id: UUID) -> RawPublication | None:
        return self.items.get(publication_id)

    async def get_by_external_id(
        self,
        source_id: UUID,
        external_id: str,
    ) -> RawPublication | None:
        return next(
            (
                item
                for item in self.items.values()
                if item.source_id == source_id and item.external_id == external_id
            ),
            None,
        )

    async def get_by_source(
        self,
        source_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RawPublication]:
        items = [item for item in self.items.values() if item.source_id == source_id]
        return items[offset : offset + limit]

    async def save(self, publication: RawPublication) -> RawPublication:
        self.items[publication.id] = publication
        return publication


class FakeRumorRepository(IRumorRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Rumor] = {}

    async def get_by_id(self, rumor_id: UUID) -> Rumor | None:
        return self.items.get(rumor_id)

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: RumorStatus | None = None,
        source_id: UUID | None = None,
        event_id: UUID | None = None,
        is_public: bool | None = None,
    ) -> list[Rumor]:
        items = list(self.items.values())
        if status is not None:
            items = [item for item in items if item.status == status]
        if source_id is not None:
            items = [item for item in items if item.source_id == source_id]
        if event_id is not None:
            items = [item for item in items if item.event_id == event_id]
        if is_public is not None:
            items = [item for item in items if item.is_public == is_public]
        return items[offset : offset + limit]

    async def save(self, rumor: Rumor) -> Rumor:
        self.items[rumor.id] = rumor
        return rumor


@pytest.fixture
def transaction_manager() -> FakeTransactionManager:
    return FakeTransactionManager()


@pytest.fixture
def source_repository() -> FakeSourceRepository:
    return FakeSourceRepository()


@pytest.fixture
def raw_publication_repository() -> FakeRawPublicationRepository:
    return FakeRawPublicationRepository()


@pytest.fixture
def rumor_repository() -> FakeRumorRepository:
    return FakeRumorRepository()


@pytest.mark.asyncio
async def test_create_source_commits_transaction(
    source_repository: FakeSourceRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    use_cases = SourceUseCases(
        source_repository=source_repository,
        source_mapper=SourceMapper(),
        transaction_manager=transaction_manager,
    )

    result = await use_cases.create_source(
        CreateSourceDTO(
            name="Karpov",
            source_type=SourceType.TELEGRAM,
            handle="@karpinside",
            weight=1.5,
        )
    )

    assert result.name == "Karpov"
    assert result.source_type == SourceType.TELEGRAM
    assert result.id in source_repository.items
    assert transaction_manager.commits == 1
    assert transaction_manager.rollbacks == 0


@pytest.mark.asyncio
async def test_create_publication_requires_existing_source(
    source_repository: FakeSourceRepository,
    raw_publication_repository: FakeRawPublicationRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    use_cases = RawPublicationUseCases(
        raw_publication_repository=raw_publication_repository,
        source_repository=source_repository,
        raw_publication_mapper=RawPublicationMapper(),
        transaction_manager=transaction_manager,
    )

    with pytest.raises(ValueError, match="Source .* not found"):
        await use_cases.create_publication(
            CreateRawPublicationDTO(source_id=uuid4(), text="Transfer rumor")
        )

    assert transaction_manager.rollbacks == 1


@pytest.mark.asyncio
async def test_create_publication_returns_existing_external_record(
    source_repository: FakeSourceRepository,
    raw_publication_repository: FakeRawPublicationRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    source = Source(id=uuid4(), name="Media", source_type=SourceType.MEDIA)
    await source_repository.save(source)
    existing = RawPublication(
        id=uuid4(),
        source_id=source.id,
        external_id="post-1",
        text="Original text",
    )
    await raw_publication_repository.save(existing)
    use_cases = RawPublicationUseCases(
        raw_publication_repository=raw_publication_repository,
        source_repository=source_repository,
        raw_publication_mapper=RawPublicationMapper(),
        transaction_manager=transaction_manager,
    )

    result = await use_cases.create_publication(
        CreateRawPublicationDTO(
            source_id=source.id,
            external_id="post-1",
            text="Duplicate text",
        )
    )

    assert result.id == existing.id
    assert result.text == "Original text"
    assert len(raw_publication_repository.items) == 1


@pytest.mark.asyncio
async def test_create_rumor_and_filter_by_status(
    source_repository: FakeSourceRepository,
    raw_publication_repository: FakeRawPublicationRepository,
    rumor_repository: FakeRumorRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    source = Source(id=uuid4(), name="Telegram", source_type=SourceType.TELEGRAM)
    await source_repository.save(source)
    use_cases = RumorUseCases(
        rumor_repository=rumor_repository,
        source_repository=source_repository,
        raw_publication_repository=raw_publication_repository,
        rumor_mapper=RumorMapper(),
        transaction_manager=transaction_manager,
    )

    created = await use_cases.create_rumor(
        CreateRumorDTO(
            source_id=source.id,
            title="Forward transfer",
            text="Forward can move in summer.",
            confidence_score=0.75,
            status=RumorStatus.CANDIDATE,
            tags=["transfer"],
        )
    )
    candidates = await use_cases.get_rumors(status=RumorStatus.CANDIDATE)
    approved = await use_cases.get_rumors(status=RumorStatus.APPROVED)

    assert created.status == RumorStatus.CANDIDATE
    assert candidates == [created]
    assert approved == []


@pytest.mark.asyncio
async def test_approved_rumor_becomes_public(
    source_repository: FakeSourceRepository,
    raw_publication_repository: FakeRawPublicationRepository,
    rumor_repository: FakeRumorRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    source = Source(id=uuid4(), name="Telegram", source_type=SourceType.TELEGRAM)
    rumor = Rumor(
        id=uuid4(),
        source_id=source.id,
        title="Coach exit",
        text="Coach can leave.",
    )
    await source_repository.save(source)
    await rumor_repository.save(rumor)
    use_cases = RumorUseCases(
        rumor_repository=rumor_repository,
        source_repository=source_repository,
        raw_publication_repository=raw_publication_repository,
        rumor_mapper=RumorMapper(),
        transaction_manager=transaction_manager,
    )

    result = await use_cases.update_status(
        rumor.id,
        UpdateRumorStatusDTO(status=RumorStatus.APPROVED),
    )
    public_rumors = await use_cases.get_rumors(is_public=True)

    assert result is not None
    assert result.is_public is True
    assert result.published_at is not None
    assert [item.id for item in public_rumors] == [rumor.id]


@pytest.mark.asyncio
async def test_update_rumor_status(
    source_repository: FakeSourceRepository,
    raw_publication_repository: FakeRawPublicationRepository,
    rumor_repository: FakeRumorRepository,
    transaction_manager: FakeTransactionManager,
) -> None:
    source = Source(id=uuid4(), name="Telegram", source_type=SourceType.TELEGRAM)
    rumor = Rumor(
        id=uuid4(),
        source_id=source.id,
        title="Coach exit",
        text="Coach can leave.",
    )
    await source_repository.save(source)
    await rumor_repository.save(rumor)
    use_cases = RumorUseCases(
        rumor_repository=rumor_repository,
        source_repository=source_repository,
        raw_publication_repository=raw_publication_repository,
        rumor_mapper=RumorMapper(),
        transaction_manager=transaction_manager,
    )

    result = await use_cases.update_status(
        rumor.id,
        UpdateRumorStatusDTO(status=RumorStatus.REJECTED),
    )

    assert result is not None
    assert result.status == RumorStatus.REJECTED
    assert rumor_repository.items[rumor.id].status == RumorStatus.REJECTED
