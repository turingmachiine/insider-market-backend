from dishka import Provider, Scope, provide

from src.domain.interfaces.repositories import ILeagueRepository, IPlayerRepository
from src.processing.matching.service import PlayerMatchingService
from src.processing.radar.service import RadarChartService
from src.processing.shadow_team.service import ShadowTeamService


class ProcessingProvider(Provider):
    """Провайдер сервисов процессинга"""

    scope = Scope.REQUEST

    @provide
    def provide_radar_service(
        self,
        player_repository: IPlayerRepository,
        league_repository: ILeagueRepository,
    ) -> RadarChartService:
        """Сервис радар-чартов"""
        return RadarChartService(player_repository, league_repository)

    @provide
    def provide_matching_service(self) -> PlayerMatchingService:
        """Сервис подбора игроков"""
        return PlayerMatchingService()

    @provide
    def provide_shadow_team_service(self) -> ShadowTeamService:
        """Сервис shadow-team"""
        return ShadowTeamService()
