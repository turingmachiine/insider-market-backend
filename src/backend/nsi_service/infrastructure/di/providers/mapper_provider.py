from dishka import Provider, Scope, provide

from src.backend.nsi_service.application.mappers import (
    IClubMapper,
    ICreatePlayerMapper,
    ILeagueMapper,
    IPlayerMapper,
    ITeamMapper,
    IUpdatePlayerMapper,
)
from src.backend.nsi_service.infrastructure.adaptix import (
    ClubMapperImpl,
    CreatePlayerMapperImpl,
    LeagueMapperImpl,
    PlayerMapperImpl,
    TeamMapperImpl,
    UpdatePlayerMapperImpl,
)
from src.backend.nsi_service.infrastructure.adaptix.response_mappers import (
    ClubResponseMapper,
    LeagueResponseMapper,
    PlayerResponseMapper,
    TeamResponseMapper,
)
from src.backend.nsi_service.presentation.api.v1.mappers import (
    IClubResponseMapper,
    ILeagueResponseMapper,
    IPlayerResponseMapper,
    ITeamResponseMapper,
)


class MapperProvider(Provider):
    """Провайдер мапперов - привязка интерфейсов к реализациям"""

    scope = Scope.REQUEST

    @provide
    def provide_player_mapper(self) -> IPlayerMapper:
        return PlayerMapperImpl()

    @provide
    def provide_create_player_mapper(self) -> ICreatePlayerMapper:
        return CreatePlayerMapperImpl()

    @provide
    def provide_update_player_mapper(self) -> IUpdatePlayerMapper:
        return UpdatePlayerMapperImpl()

    @provide
    def provide_club_mapper(self) -> IClubMapper:
        return ClubMapperImpl()

    @provide
    def provide_league_mapper(self) -> ILeagueMapper:
        return LeagueMapperImpl()

    @provide
    def provide_team_mapper(self) -> ITeamMapper:
        return TeamMapperImpl()

    @provide
    def provide_player_response_mapper(self) -> IPlayerResponseMapper:
        return PlayerResponseMapper()

    @provide
    def provide_team_response_mapper(self) -> ITeamResponseMapper:
        return TeamResponseMapper()

    @provide
    def provide_club_response_mapper(self) -> IClubResponseMapper:
        return ClubResponseMapper()

    @provide
    def provide_league_response_mapper(self) -> ILeagueResponseMapper:
        return LeagueResponseMapper()
