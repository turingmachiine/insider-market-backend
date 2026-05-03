from uuid import UUID, uuid4

from src.backend.common.application.decorators import transactional, use_case
from src.backend.common.application.protocols import HasTransactionManager
from src.backend.common.domain.interfaces import TransactionManager
from src.backend.rumor_service.application.dto import CreateSourceDTO, SourceDTO
from src.backend.rumor_service.application.mappers import ISourceMapper
from src.backend.rumor_service.domain.entities import Source
from src.backend.rumor_service.domain.interfaces.repositories import ISourceRepository


@use_case
class SourceUseCases(HasTransactionManager):
    source_repository: ISourceRepository
    source_mapper: ISourceMapper
    transaction_manager: TransactionManager

    async def get_source(self, source_id: UUID) -> SourceDTO | None:
        source = await self.source_repository.get_by_id(source_id)
        return self.source_mapper.to_dto(source) if source else None

    async def get_sources(
        self,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
    ) -> list[SourceDTO]:
        sources = await self.source_repository.get_all(
            limit=limit,
            offset=offset,
            active_only=active_only,
        )
        return [self.source_mapper.to_dto(source) for source in sources]

    @transactional()
    async def create_source(self, dto: CreateSourceDTO) -> SourceDTO:
        source = Source(
            id=uuid4(),
            name=dto.name,
            source_type=dto.source_type,
            handle=dto.handle,
            url=dto.url,
            weight=dto.weight,
            is_active=dto.is_active,
        )
        saved_source = await self.source_repository.save(source)
        return self.source_mapper.to_dto(saved_source)
