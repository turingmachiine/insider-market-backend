from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.admin_service.domain.interfaces.repositories import (
    IAdminActionRepository,
    ISavedFilterRepository,
)
from src.backend.admin_service.infrastructure.db.repositories import (
    AdminActionRepository,
    SavedFilterRepository,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_admin_action_repository(
        session: AsyncSession,
    ) -> IAdminActionRepository:
        return AdminActionRepository(session)

    @provide
    @staticmethod
    def provide_saved_filter_repository(
        session: AsyncSession,
    ) -> ISavedFilterRepository:
        return SavedFilterRepository(session)
