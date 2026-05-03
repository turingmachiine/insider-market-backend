from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.rumor_service.domain.interfaces.repositories import (
    IRawPublicationRepository,
    IRumorRepository,
    ISourceRepository,
)
from src.backend.rumor_service.infrastructure.db.repositories import (
    RawPublicationRepository,
    RumorRepository,
    SourceRepository,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_source_repository(self, session: AsyncSession) -> ISourceRepository:
        return SourceRepository(session)

    @provide
    def provide_raw_publication_repository(
        self,
        session: AsyncSession,
    ) -> IRawPublicationRepository:
        return RawPublicationRepository(session)

    @provide
    def provide_rumor_repository(self, session: AsyncSession) -> IRumorRepository:
        return RumorRepository(session)
