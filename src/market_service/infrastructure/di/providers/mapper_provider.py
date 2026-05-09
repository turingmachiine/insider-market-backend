from dishka import Provider, Scope, provide

from src.market_service.application.mappers import (
    BetMapper,
    IBetMapper,
    IMarketMapper,
    IPositionMapper,
    IWalletMapper,
    MarketMapper,
    PositionMapper,
    WalletMapper,
)


class MapperProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def provide_market_mapper() -> IMarketMapper:
        return MarketMapper()

    @provide
    @staticmethod
    def provide_bet_mapper() -> IBetMapper:
        return BetMapper()

    @provide
    @staticmethod
    def provide_position_mapper() -> IPositionMapper:
        return PositionMapper()

    @provide
    @staticmethod
    def provide_wallet_mapper() -> IWalletMapper:
        return WalletMapper()
