from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.nsi_service.domain.interfaces.repositories import (
    IClubRepository,
    ILeagueRepository,
    IPlayerRepository,
    ITeamRepository,
)
from src.backend.nsi_service.infrastructure.db.repositories import (
    ClubRepository,
    LeagueRepository,
    PlayerRepository,
    TeamRepository,
)


class RepositoryProvider(Provider):
    """Провайдер репозиториев"""

    scope = Scope.REQUEST

    @provide
    def provide_player_repository(
        self,
        session: AsyncSession,
    ) -> IPlayerRepository:
        """Репозиторий игроков"""
        return PlayerRepository(session)

    @provide
    def provide_club_repository(
        self,
        session: AsyncSession,
    ) -> IClubRepository:
        """Репозиторий клубов"""
        return ClubRepository(session)

    @provide
    def provide_league_repository(
        self,
        session: AsyncSession,
    ) -> ILeagueRepository:
        """Репозиторий лиг"""
        return LeagueRepository(session)

    @provide
    def provide_team_repository(
        self,
        session: AsyncSession,
    ) -> ITeamRepository:
        """Репозиторий команд"""
        return TeamRepository(session)
