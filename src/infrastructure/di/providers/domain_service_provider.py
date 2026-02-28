from dishka import Provider, Scope, provide

from src.domain.services import PlayerService, TeamService


class DomainServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_player_service(self) -> PlayerService:
        return PlayerService()

    @provide
    def provide_team_service(self) -> TeamService:
        return TeamService()
