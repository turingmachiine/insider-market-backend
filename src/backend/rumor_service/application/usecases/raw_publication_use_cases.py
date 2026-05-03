from uuid import UUID, uuid4

from src.backend.common.application.decorators import transactional, use_case
from src.backend.common.application.protocols import HasTransactionManager
from src.backend.common.domain.interfaces import TransactionManager
from src.backend.rumor_service.application.dto import (
    CreateRawPublicationDTO,
    RawPublicationDTO,
)
from src.backend.rumor_service.application.mappers import IRawPublicationMapper
from src.backend.rumor_service.domain.entities import RawPublication
from src.backend.rumor_service.domain.interfaces.repositories import (
    IRawPublicationRepository,
    ISourceRepository,
)


@use_case
class RawPublicationUseCases(HasTransactionManager):
    raw_publication_repository: IRawPublicationRepository
    source_repository: ISourceRepository
    raw_publication_mapper: IRawPublicationMapper
    transaction_manager: TransactionManager

    async def get_publication(self, publication_id: UUID) -> RawPublicationDTO | None:
        publication = await self.raw_publication_repository.get_by_id(publication_id)
        return self.raw_publication_mapper.to_dto(publication) if publication else None

    async def get_publications_by_source(
        self,
        source_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RawPublicationDTO]:
        publications = await self.raw_publication_repository.get_by_source(
            source_id=source_id,
            limit=limit,
            offset=offset,
        )
        return [self.raw_publication_mapper.to_dto(item) for item in publications]

    @transactional()
    async def create_publication(
        self,
        dto: CreateRawPublicationDTO,
    ) -> RawPublicationDTO:
        source = await self.source_repository.get_by_id(dto.source_id)
        if source is None:
            raise ValueError(f"Source {str(dto.source_id)} not found")

        if dto.external_id:
            existing = await self.raw_publication_repository.get_by_external_id(
                source_id=dto.source_id,
                external_id=dto.external_id,
            )
            if existing is not None:
                return self.raw_publication_mapper.to_dto(existing)

        publication = RawPublication(
            id=uuid4(),
            source_id=dto.source_id,
            text=dto.text,
            external_id=dto.external_id,
            url=dto.url,
            published_at=dto.published_at,
            payload=dto.payload,
        )
        saved_publication = await self.raw_publication_repository.save(publication)
        return self.raw_publication_mapper.to_dto(saved_publication)
