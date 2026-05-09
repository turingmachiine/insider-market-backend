from uuid import UUID, uuid4

from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager
from src.event_service.application.dto import (
    CancelEventDTO,
    CreateEventDTO,
    EventDTO,
    RejectEventDTO,
    ResolveEventDTO,
    UpdateEventDTO,
)
from src.event_service.application.mappers import IEventMapper
from src.event_service.domain.entities import Event, EventStatus
from src.event_service.domain.interfaces.repositories import IEventRepository


@use_case
class EventUseCases(HasTransactionManager):
    event_repository: IEventRepository
    event_mapper: IEventMapper
    transaction_manager: TransactionManager

    async def get_event(self, event_id: UUID) -> EventDTO | None:
        event = await self.event_repository.get_by_id(event_id)
        return self.event_mapper.to_dto(event) if event else None

    async def get_events(
        self,
        limit: int = 100,
        offset: int = 0,
        status: EventStatus | None = None,
        source_rumor_id: UUID | None = None,
    ) -> list[EventDTO]:
        events = await self.event_repository.get_all(
            limit=limit,
            offset=offset,
            status=status,
            source_rumor_id=source_rumor_id,
        )
        return [self.event_mapper.to_dto(event) for event in events]

    async def get_moderation_queue(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EventDTO]:
        return await self.get_events(
            limit=limit,
            offset=offset,
            status=EventStatus.PENDING_MODERATION,
        )

    @transactional()
    async def create_event(self, dto: CreateEventDTO) -> EventDTO:
        event = Event(
            id=uuid4(),
            title=dto.title,
            description=dto.description,
            source_rumor_id=dto.source_rumor_id,
            candidate_payload=dto.candidate_payload,
            deadline_at=dto.deadline_at,
            resolution_rules=dto.resolution_rules,
            created_by_user_id=dto.created_by_user_id,
        )
        if dto.submit_for_moderation:
            event.submit_for_moderation()
        saved_event = await self.event_repository.save(event)
        return self.event_mapper.to_dto(saved_event)

    @transactional()
    async def update_event(
        self,
        event_id: UUID,
        dto: UpdateEventDTO,
    ) -> EventDTO | None:
        event = await self.event_repository.get_by_id(event_id)
        if event is None:
            return None
        event.update_details(
            title=dto.title,
            description=dto.description,
            deadline_at=dto.deadline_at,
            resolution_rules=dto.resolution_rules,
            candidate_payload=dto.candidate_payload,
        )
        saved_event = await self.event_repository.save(event)
        return self.event_mapper.to_dto(saved_event)

    @transactional()
    async def submit_for_moderation(self, event_id: UUID) -> EventDTO | None:
        event = await self.event_repository.get_by_id(event_id)
        if event is None:
            return None
        event.submit_for_moderation()
        saved_event = await self.event_repository.save(event)
        return self.event_mapper.to_dto(saved_event)

    @transactional()
    async def approve_event(self, event_id: UUID) -> EventDTO | None:
        event = await self.event_repository.get_by_id(event_id)
        if event is None:
            return None
        event.approve()
        saved_event = await self.event_repository.save(event)
        return self.event_mapper.to_dto(saved_event)

    @transactional()
    async def reject_event(
        self,
        event_id: UUID,
        dto: RejectEventDTO,
    ) -> EventDTO | None:
        event = await self.event_repository.get_by_id(event_id)
        if event is None:
            return None
        event.reject(notes=dto.notes)
        saved_event = await self.event_repository.save(event)
        return self.event_mapper.to_dto(saved_event)

    @transactional()
    async def resolve_event(
        self,
        event_id: UUID,
        dto: ResolveEventDTO,
    ) -> EventDTO | None:
        event = await self.event_repository.get_by_id(event_id)
        if event is None:
            return None
        event.resolve(
            outcome=dto.outcome,
            resolved_by_user_id=dto.resolved_by_user_id,
            notes=dto.notes,
        )
        saved_event = await self.event_repository.save(event)
        return self.event_mapper.to_dto(saved_event)

    @transactional()
    async def cancel_event(
        self,
        event_id: UUID,
        dto: CancelEventDTO,
    ) -> EventDTO | None:
        event = await self.event_repository.get_by_id(event_id)
        if event is None:
            return None
        event.cancel(notes=dto.notes)
        saved_event = await self.event_repository.save(event)
        return self.event_mapper.to_dto(saved_event)
