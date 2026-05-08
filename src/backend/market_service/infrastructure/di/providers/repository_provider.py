from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.market_service.domain.interfaces.repositories import (
    IBetRepository,
    IMarketRepository,
    IPositionRepository,
    IWalletRepository,
)
from src.backend.market_service.infrastructure.db.repositories import (
    BetRepository,
    MarketRepository,
    PositionRepository,
    WalletRepository,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_market_repository(session: AsyncSession) -> IMarketRepository:
        return MarketRepository(session)

    @provide
    @staticmethod
    def provide_bet_repository(session: AsyncSession) -> IBetRepository:
        return BetRepository(session)

    @provide
    @staticmethod
    def provide_position_repository(session: AsyncSession) -> IPositionRepository:
        return PositionRepository(session)

    @provide
    @staticmethod
    def provide_wallet_repository(session: AsyncSession) -> IWalletRepository:
        return WalletRepository(session)
