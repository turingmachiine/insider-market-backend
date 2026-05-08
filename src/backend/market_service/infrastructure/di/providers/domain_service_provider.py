from dishka import Provider, Scope, provide

from src.backend.market_service.domain.services import AMMService


class DomainServiceProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_amm_service() -> AMMService:
        return AMMService()
