from uuid import UUID, uuid4

from src.backend.common.application.decorators import transactional, use_case
from src.backend.common.application.protocols import HasTransactionManager
from src.backend.common.domain.interfaces import TransactionManager
from src.backend.rumor_service.application.dto import (
    CreateRumorDTO,
    RumorDTO,
    UpdateRumorStatusDTO,
)
from src.backend.rumor_service.application.mappers import IRumorMapper
from src.backend.rumor_service.domain.entities import Rumor, RumorStatus
from src.backend.rumor_service.domain.interfaces.repositories import (
    IRawPublicationRepository,
    IRumorRepository,
    ISourceRepository,
)


@use_case
class RumorUseCases(HasTransactionManager):
    rumor_repository: IRumorRepository
    source_repository: ISourceRepository
    raw_publication_repository: IRawPublicationRepository
    rumor_mapper: IRumorMapper
    transaction_manager: TransactionManager

    async def get_rumor(self, rumor_id: UUID) -> RumorDTO | None:
        rumor = await self.rumor_repository.get_by_id(rumor_id)
        return self.rumor_mapper.to_dto(rumor) if rumor else None

    async def get_rumors(
        self,
        limit: int = 100,
        offset: int = 0,
        status: RumorStatus | None = None,
        source_id: UUID | None = None,
    ) -> list[RumorDTO]:
        rumors = await self.rumor_repository.get_all(
            limit=limit,
            offset=offset,
            status=status,
            source_id=source_id,
        )
        return [self.rumor_mapper.to_dto(rumor) for rumor in rumors]

    @transactional()
    async def create_rumor(self, dto: CreateRumorDTO) -> RumorDTO:
        source = await self.source_repository.get_by_id(dto.source_id)
        if source is None:
            raise ValueError(f"Source {str(dto.source_id)} not found")

        if dto.raw_publication_id is not None:
            publication = await self.raw_publication_repository.get_by_id(
                dto.raw_publication_id
            )
            if publication is None:
                raise ValueError(f"Publication {str(dto.raw_publication_id)} not found")

        rumor = Rumor(
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
        )
        saved_rumor = await self.rumor_repository.save(rumor)
        return self.rumor_mapper.to_dto(saved_rumor)

    @transactional()
    async def update_status(
        self,
        rumor_id: UUID,
        dto: UpdateRumorStatusDTO,
    ) -> RumorDTO | None:
        rumor = await self.rumor_repository.get_by_id(rumor_id)
        if rumor is None:
            return None
        rumor.status = dto.status
        saved_rumor = await self.rumor_repository.save(rumor)
        return self.rumor_mapper.to_dto(saved_rumor)
