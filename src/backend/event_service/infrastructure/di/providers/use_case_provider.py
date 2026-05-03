from dishka import Provider, Scope, provide

from src.backend.common.domain.interfaces import TransactionManager
from src.backend.event_service.application.mappers import IEventMapper
from src.backend.event_service.application.usecases import EventUseCases
from src.backend.event_service.domain.interfaces.repositories import IEventRepository


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_event_use_cases(
        self,
        event_repository: IEventRepository,
        event_mapper: IEventMapper,
        transaction_manager: TransactionManager,
    ) -> EventUseCases:
        return EventUseCases(
            event_repository=event_repository,
            event_mapper=event_mapper,
            transaction_manager=transaction_manager,
        )
