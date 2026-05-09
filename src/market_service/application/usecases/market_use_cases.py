from decimal import Decimal
from uuid import UUID, uuid4

from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager
from src.market_service.application.dto import (
    BetDTO,
    CreateMarketDTO,
    MarketDTO,
    PlaceBetDTO,
    PositionDTO,
    ResolveMarketDTO,
)
from src.market_service.application.mappers import (
    IBetMapper,
    IMarketMapper,
    IPositionMapper,
)
from src.market_service.domain.entities import (
    Bet,
    Market,
    MarketOutcome,
    MarketSide,
    MarketStatus,
    Position,
)
from src.market_service.domain.interfaces.repositories import (
    IBetRepository,
    IMarketRepository,
    IPositionRepository,
    IWalletRepository,
)
from src.market_service.domain.services import AMMService


@use_case
class MarketUseCases(HasTransactionManager):
    market_repository: IMarketRepository
    bet_repository: IBetRepository
    position_repository: IPositionRepository
    wallet_repository: IWalletRepository
    market_mapper: IMarketMapper
    bet_mapper: IBetMapper
    position_mapper: IPositionMapper
    amm_service: AMMService
    transaction_manager: TransactionManager

    async def get_market(self, market_id: UUID) -> MarketDTO | None:
        market = await self.market_repository.get_by_id(market_id)
        return self.market_mapper.to_dto(market) if market else None

    async def get_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        status: MarketStatus | None = None,
        event_id: UUID | None = None,
    ) -> list[MarketDTO]:
        markets = await self.market_repository.get_all(
            limit=limit,
            offset=offset,
            status=status,
            event_id=event_id,
        )
        return [self.market_mapper.to_dto(market) for market in markets]

    async def get_market_bets(
        self,
        market_id: UUID,
        limit: int = 100,
        offset: int = 0,
        user_id: UUID | None = None,
    ) -> list[BetDTO]:
        bets = await self.bet_repository.get_by_market(
            market_id=market_id,
            limit=limit,
            offset=offset,
            user_id=user_id,
        )
        return [self.bet_mapper.to_dto(bet) for bet in bets]

    async def get_market_positions(self, market_id: UUID) -> list[PositionDTO]:
        positions = await self.position_repository.get_by_market(market_id)
        return [self.position_mapper.to_dto(position) for position in positions]

    @transactional()
    async def create_market(self, dto: CreateMarketDTO) -> MarketDTO:
        """Создает рынок и переводит начальную вероятность в AMM-пулы."""
        existing_market = await self.market_repository.get_by_event_id(dto.event_id)
        if existing_market is not None:
            raise ValueError(f"Market for event {str(dto.event_id)} already exists")

        yes_pool, no_pool = self.amm_service.create_initial_pools(
            initial_probability=dto.initial_probability,
            liquidity_parameter=dto.liquidity_parameter,
        )
        market = Market(
            id=uuid4(),
            event_id=dto.event_id,
            title=dto.title,
            description=dto.description,
            initial_probability=dto.initial_probability,
            liquidity_parameter=dto.liquidity_parameter,
            yes_pool=yes_pool,
            no_pool=no_pool,
            close_at=dto.close_at,
            created_by_user_id=dto.created_by_user_id,
        )
        if dto.activate:
            market.activate()
        saved_market = await self.market_repository.save(market)
        return self.market_mapper.to_dto(saved_market)

    @transactional()
    async def place_bet(self, market_id: UUID, dto: PlaceBetDTO) -> BetDTO:
        """Проводит покупку shares как единую транзакцию.

        Use case получает quote от AMM, списывает нормализованную сумму с
        кошелька, применяет новые пулы к рынку, обновляет позицию пользователя
        и сохраняет аудит сделки в Bet. Важно использовать quote.amount, а не
        исходный dto.amount, потому что quote уже округлен до шага коина.
        """
        market = await self.market_repository.get_by_id(market_id)
        if market is None:
            raise ValueError(f"Market {str(market_id)} not found")
        if market.status != MarketStatus.ACTIVE:
            raise ValueError(f"Market {str(market_id)} is not active")

        wallet = await self.wallet_repository.get_by_user_id(dto.user_id)
        if wallet is None:
            raise ValueError(f"Wallet for user {str(dto.user_id)} not found")

        quote = self.amm_service.quote_buy(
            market=market,
            side=dto.side,
            amount=dto.amount,
        )
        wallet.debit(quote.amount)
        self.amm_service.apply_quote(market, quote)

        position = await self.position_repository.get_by_market_user_side(
            market_id=market_id,
            user_id=dto.user_id,
            side=dto.side,
        )
        if position is None:
            position = Position(
                id=uuid4(),
                market_id=market_id,
                user_id=dto.user_id,
                side=dto.side,
            )
        position.add_trade(amount=quote.amount, shares=quote.shares)

        bet = Bet(
            id=uuid4(),
            market_id=market_id,
            user_id=dto.user_id,
            side=dto.side,
            amount=quote.amount,
            shares=quote.shares,
            probability_before=quote.probability_before,
            probability_after=quote.probability_after,
            odds_before=quote.odds_before,
            odds_after=quote.odds_after,
        )
        await self.wallet_repository.save(wallet)
        await self.position_repository.save(position)
        await self.market_repository.save(market)
        saved_bet = await self.bet_repository.save(bet)
        return self.bet_mapper.to_dto(saved_bet)

    @transactional()
    async def close_market(self, market_id: UUID) -> MarketDTO | None:
        market = await self.market_repository.get_by_id(market_id)
        if market is None:
            return None
        market.close()
        saved_market = await self.market_repository.save(market)
        return self.market_mapper.to_dto(saved_market)

    @transactional()
    async def resolve_market(
        self,
        market_id: UUID,
        dto: ResolveMarketDTO,
    ) -> MarketDTO | None:
        """Фиксирует outcome рынка и рассчитывает выплаты по всем позициям."""
        market = await self.market_repository.get_by_id(market_id)
        if market is None:
            return None

        positions = await self.position_repository.get_by_market(market_id)
        market.resolve(
            outcome=dto.outcome,
            resolved_by_user_id=dto.resolved_by_user_id,
        )
        await self._settle_positions(positions, dto.outcome)
        saved_market = await self.market_repository.save(market)
        return self.market_mapper.to_dto(saved_market)

    async def _settle_positions(
        self,
        positions: list[Position],
        outcome: MarketOutcome,
    ) -> None:
        """Начисляет payout на кошельки и помечает позиции рассчитанными.

        Для победившей стороны shares выплачиваются один к одному в коинах.
        При VOID возвращается invested amount, а проигравшие стороны получают
        нулевой payout.
        """
        for position in positions:
            payout = self._calculate_payout(position, outcome)
            position.settle(payout)
            wallet = await self.wallet_repository.get_by_user_id(position.user_id)
            if wallet is None:
                raise ValueError(f"Wallet for user {str(position.user_id)} not found")
            wallet.credit(payout)
            await self.wallet_repository.save(wallet)
            await self.position_repository.save(position)

    @staticmethod
    def _calculate_payout(
        position: Position,
        outcome: MarketOutcome,
    ) -> Decimal:
        """Возвращает сумму выплаты для позиции с учетом итогового outcome."""
        if outcome == MarketOutcome.VOID:
            return position.invested_amount
        if outcome == MarketOutcome.YES and position.side == MarketSide.YES:
            return position.shares
        if outcome == MarketOutcome.NO and position.side == MarketSide.NO:
            return position.shares
        return Decimal("0")


__all__ = ["MarketUseCases"]
