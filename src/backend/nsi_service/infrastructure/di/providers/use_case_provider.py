from dishka import Provider, Scope, provide

from src.backend.common.domain.interfaces import TransactionManager
from src.backend.nsi_service.application.mappers import (
    IClubMapper,
    ICreatePlayerMapper,
    ILeagueMapper,
    IPlayerMapper,
    ITeamMapper,
    IUpdatePlayerMapper,
)
from src.backend.nsi_service.application.usecases import (
    ClubUseCases,
    LeagueUseCases,
    PlayerUseCases,
    TeamUseCases,
)
from src.backend.nsi_service.domain.interfaces.repositories import (
    IClubRepository,
    ILeagueRepository,
    IPlayerRepository,
    ITeamRepository,
)
from src.backend.nsi_service.domain.services import TeamService
from src.backend.nsi_service.processing.matching.service import PlayerMatchingService
from src.backend.nsi_service.processing.radar.service import RadarChartService
from src.backend.nsi_service.processing.shadow_team.service import ShadowTeamService


class UseCaseProvider(Provider):
    """Провайдер use cases"""

    scope = Scope.REQUEST

    @provide
    def provide_player_use_cases(
        self,
        player_repository: IPlayerRepository,
        club_repository: IClubRepository,
        league_repository: ILeagueRepository,
        radar_service: RadarChartService,
        matching_service: PlayerMatchingService,
        player_mapper: IPlayerMapper,
        create_player_mapper: ICreatePlayerMapper,
        update_player_mapper: IUpdatePlayerMapper,
        transaction_manager: TransactionManager,
    ) -> PlayerUseCases:
        """Use cases для игроков"""
        return PlayerUseCases(
            player_repository=player_repository,
            club_repository=club_repository,
            league_repository=league_repository,
            radar_service=radar_service,
            matching_service=matching_service,
            player_mapper=player_mapper,
            create_player_mapper=create_player_mapper,
            update_player_mapper=update_player_mapper,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_club_use_cases(
        self,
        club_repository: IClubRepository,
        player_repository: IPlayerRepository,
        club_mapper: IClubMapper,
        transaction_manager: TransactionManager,
    ) -> ClubUseCases:
        """Use cases для клубов"""
        return ClubUseCases(
            club_repository=club_repository,
            player_repository=player_repository,
            club_mapper=club_mapper,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_league_use_cases(
        self,
        league_repository: ILeagueRepository,
        league_mapper: ILeagueMapper,
        transaction_manager: TransactionManager,
    ) -> LeagueUseCases:
        """Use cases для лиг"""
        return LeagueUseCases(
            league_repository=league_repository,
            league_mapper=league_mapper,
            transaction_manager=transaction_manager,
        )

    @provide
    def provide_team_use_cases(
        self,
        team_repository: ITeamRepository,
        player_repository: IPlayerRepository,
        shadow_team_service: ShadowTeamService,
        team_service: TeamService,
        team_mapper: ITeamMapper,
        transaction_manager: TransactionManager,
    ) -> TeamUseCases:
        """Use cases для команд"""
        return TeamUseCases(
            team_repository=team_repository,
            player_repository=player_repository,
            shadow_team_service=shadow_team_service,
            team_service=team_service,
            team_mapper=team_mapper,
            transaction_manager=transaction_manager,
        )
