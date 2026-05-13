from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.market_service.domain.interfaces.repositories import (
    IAuditLogRepository,
    IBetRepository,
    IMarketRepository,
    IPositionRepository,
    IWalletRepository,
)
from src.market_service.infrastructure.db.repositories import (
    AuditLogRepository,
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
    def provide_audit_log_repository(session: AsyncSession) -> IAuditLogRepository:
        return AuditLogRepository(session)

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
