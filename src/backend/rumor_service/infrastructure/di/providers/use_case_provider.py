from dishka import Provider, Scope, provide

from src.backend.common.domain.interfaces import TransactionManager
from src.backend.rumor_service.application.mappers import (
    IRawPublicationMapper,
    IRumorMapper,
    ISourceMapper,
)
from src.backend.rumor_service.application.usecases import (
    RawPublicationUseCases,
    RumorUseCases,
    SourceUseCases,
)
from src.backend.rumor_service.domain.interfaces.repositories import (
    IRawPublicationRepository,
    IRumorRepository,
    ISourceRepository,
)


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_source_use_cases(
        self,
        source_repository: ISourceRepository,
        source_mapper: ISourceMapper,
        transaction_manager: TransactionManager,
    ) -> SourceUseCases:
        return SourceUseCases(
            source_repository=source_repository,
            source_mapper=source_mapper,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_raw_publication_use_cases(
        self,
        raw_publication_repository: IRawPublicationRepository,
        source_repository: ISourceRepository,
        raw_publication_mapper: IRawPublicationMapper,
        transaction_manager: TransactionManager,
    ) -> RawPublicationUseCases:
        return RawPublicationUseCases(
            raw_publication_repository=raw_publication_repository,
            source_repository=source_repository,
            raw_publication_mapper=raw_publication_mapper,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_rumor_use_cases(
        self,
        rumor_repository: IRumorRepository,
        source_repository: ISourceRepository,
        raw_publication_repository: IRawPublicationRepository,
        rumor_mapper: IRumorMapper,
        transaction_manager: TransactionManager,
    ) -> RumorUseCases:
        return RumorUseCases(
            rumor_repository=rumor_repository,
            source_repository=source_repository,
            raw_publication_repository=raw_publication_repository,
            rumor_mapper=rumor_mapper,
            transaction_manager=transaction_manager,
        )
