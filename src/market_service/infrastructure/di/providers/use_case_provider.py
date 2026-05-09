from dishka import Provider, Scope, provide

from src.common.domain.interfaces import TransactionManager
from src.market_service.application.mappers import (
    IBetMapper,
    IMarketMapper,
    IPositionMapper,
    IWalletMapper,
)
from src.market_service.application.usecases import MarketUseCases, WalletUseCases
from src.market_service.domain.interfaces.repositories import (
    IBetRepository,
    IMarketRepository,
    IPositionRepository,
    IWalletRepository,
)
from src.market_service.domain.services import AMMService


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_market_use_cases(
        market_repository: IMarketRepository,
        bet_repository: IBetRepository,
        position_repository: IPositionRepository,
        wallet_repository: IWalletRepository,
        market_mapper: IMarketMapper,
        bet_mapper: IBetMapper,
        position_mapper: IPositionMapper,
        amm_service: AMMService,
        transaction_manager: TransactionManager,
    ) -> MarketUseCases:
        return MarketUseCases(
            market_repository=market_repository,
            bet_repository=bet_repository,
            position_repository=position_repository,
            wallet_repository=wallet_repository,
            market_mapper=market_mapper,
            bet_mapper=bet_mapper,
            position_mapper=position_mapper,
            amm_service=amm_service,
            transaction_manager=transaction_manager,
        )

    @provide
    @staticmethod
    def provide_wallet_use_cases(
        wallet_repository: IWalletRepository,
        wallet_mapper: IWalletMapper,
        transaction_manager: TransactionManager,
    ) -> WalletUseCases:
        return WalletUseCases(
            wallet_repository=wallet_repository,
            wallet_mapper=wallet_mapper,
            transaction_manager=transaction_manager,
        )
