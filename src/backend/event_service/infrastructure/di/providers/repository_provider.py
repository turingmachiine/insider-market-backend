from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.event_service.domain.interfaces.repositories import IEventRepository
from src.backend.event_service.infrastructure.db.repositories import EventRepository


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_event_repository(self, session: AsyncSession) -> IEventRepository:
        return EventRepository(session)
