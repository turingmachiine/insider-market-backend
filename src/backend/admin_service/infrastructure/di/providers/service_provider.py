from dishka import Provider, Scope, provide

from src.backend.admin_service.application.mappers import AdminMapper
from src.backend.admin_service.application.ports import AdminGatewayClient
from src.backend.admin_service.application.usecases import AdminUseCases
from src.backend.admin_service.domain.interfaces.repositories import (
    IAdminActionRepository,
    ISavedFilterRepository,
)
from src.backend.common.domain.interfaces import TransactionManager


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_admin_use_cases(
        gateway_client: AdminGatewayClient,
        action_repository: IAdminActionRepository,
        filter_repository: ISavedFilterRepository,
        mapper: AdminMapper,
        transaction_manager: TransactionManager,
    ) -> AdminUseCases:
        return AdminUseCases(
            gateway_client=gateway_client,
            action_repository=action_repository,
            filter_repository=filter_repository,
            mapper=mapper,
            transaction_manager=transaction_manager,
        )
