from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.common.domain.interfaces import TransactionManager
from src.market_service.application.dto import (
    CreateMarketDTO,
    CreateWalletDTO,
    PlaceBetDTO,
    ResolveMarketDTO,
)
from src.market_service.application.mappers import (
    BetMapper,
    MarketMapper,
    PositionMapper,
    WalletMapper,
)
from src.market_service.application.usecases import MarketUseCases, WalletUseCases
from src.market_service.domain.entities import (
    Bet,
    Market,
    MarketOutcome,
    MarketSide,
    MarketStatus,
    Position,
    Wallet,
)
from src.market_service.domain.interfaces.repositories import (
    IBetRepository,
    IMarketRepository,
    IPositionRepository,
    IWalletRepository,
)
from src.market_service.domain.services import AMMService


class FakeTransactionManager(TransactionManager):
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.flushes = 0
        self._in_transaction = False
        self._in_nested = False

    async def begin(self) -> None:
        self._in_transaction = True

    async def begin_nested(self) -> None:
        self._in_nested = True

    async def commit(self) -> None:
        self.commits += 1
        self._in_transaction = False
        self._in_nested = False

    async def rollback(self) -> None:
        self.rollbacks += 1
        self._in_transaction = False
        self._in_nested = False

    async def flush(self) -> None:
        self.flushes += 1

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    @property
    def in_nested(self) -> bool:
        return self._in_nested


class FakeMarketRepository(IMarketRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Market] = {}

    async def get_by_id(self, market_id: UUID) -> Market | None:
        return self.items.get(market_id)

    async def get_by_event_id(self, event_id: UUID) -> Market | None:
        return next(
            (market for market in self.items.values() if market.event_id == event_id),
            None,
        )

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: MarketStatus | None = None,
        event_id: UUID | None = None,
    ) -> list[Market]:
        items = list(self.items.values())
        if status is not None:
            items = [item for item in items if item.status == status]
        if event_id is not None:
            items = [item for item in items if item.event_id == event_id]
        return items[offset : offset + limit]

    async def save(self, market: Market) -> Market:
        self.items[market.id] = market
        return market


class FakeBetRepository(IBetRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Bet] = {}

    async def get_by_market(
        self,
        market_id: UUID,
        limit: int = 100,
        offset: int = 0,
        user_id: UUID | None = None,
    ) -> list[Bet]:
        items = [item for item in self.items.values() if item.market_id == market_id]
        if user_id is not None:
            items = [item for item in items if item.user_id == user_id]
        return items[offset : offset + limit]

    async def save(self, bet: Bet) -> Bet:
        self.items[bet.id] = bet
        return bet


class FakePositionRepository(IPositionRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Position] = {}

    async def get_by_market_user_side(
        self,
        market_id: UUID,
        user_id: UUID,
        side: MarketSide,
    ) -> Position | None:
        return next(
            (
                position
                for position in self.items.values()
                if position.market_id == market_id
                and position.user_id == user_id
                and position.side == side
            ),
            None,
        )

    async def get_by_market(self, market_id: UUID) -> list[Position]:
        return [
            position
            for position in self.items.values()
            if position.market_id == market_id
        ]

    async def get_by_user(self, user_id: UUID) -> list[Position]:
        return [
            position for position in self.items.values() if position.user_id == user_id
        ]

    async def save(self, position: Position) -> Position:
        self.items[position.id] = position
        return position


class FakeWalletRepository(IWalletRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Wallet] = {}

    async def get_by_user_id(self, user_id: UUID) -> Wallet | None:
        return next(
            (wallet for wallet in self.items.values() if wallet.user_id == user_id),
            None,
        )

    async def save(self, wallet: Wallet) -> Wallet:
        self.items[wallet.id] = wallet
        return wallet


def create_market_use_cases(
    market_repository: FakeMarketRepository,
    bet_repository: FakeBetRepository,
    position_repository: FakePositionRepository,
    wallet_repository: FakeWalletRepository,
    transaction_manager: FakeTransactionManager,
) -> MarketUseCases:
    return MarketUseCases(
        market_repository=market_repository,
        bet_repository=bet_repository,
        position_repository=position_repository,
        wallet_repository=wallet_repository,
        market_mapper=MarketMapper(),
        bet_mapper=BetMapper(),
        position_mapper=PositionMapper(),
        amm_service=AMMService(),
        transaction_manager=transaction_manager,
    )


@pytest.mark.asyncio
async def test_create_wallet_and_place_bet_updates_market_state() -> None:
    market_repository = FakeMarketRepository()
    bet_repository = FakeBetRepository()
    position_repository = FakePositionRepository()
    wallet_repository = FakeWalletRepository()
    transaction_manager = FakeTransactionManager()
    wallet_use_cases = WalletUseCases(
        wallet_repository=wallet_repository,
        wallet_mapper=WalletMapper(),
        transaction_manager=transaction_manager,
    )
    market_use_cases = create_market_use_cases(
        market_repository,
        bet_repository,
        position_repository,
        wallet_repository,
        transaction_manager,
    )
    user_id = uuid4()
    await wallet_use_cases.create_wallet(
        CreateWalletDTO(user_id=user_id, initial_balance=Decimal("1000"))
    )
    market = await market_use_cases.create_market(
        CreateMarketDTO(
            event_id=uuid4(),
            title="Forward transfer",
            description="Forward can move in summer.",
            initial_probability=0.25,
            liquidity_parameter=Decimal("1000"),
        )
    )

    bet = await market_use_cases.place_bet(
        market.id,
        PlaceBetDTO(user_id=user_id, side=MarketSide.YES, amount=Decimal("100")),
    )

    wallet = await wallet_repository.get_by_user_id(user_id)
    assert market_repository.items[market.id].yes_probability > 0.25
    assert bet.shares > 0
    assert wallet is not None
    assert wallet.balance == Decimal("900.000000")


@pytest.mark.asyncio
async def test_resolve_market_pays_winning_shares() -> None:
    market_repository = FakeMarketRepository()
    bet_repository = FakeBetRepository()
    position_repository = FakePositionRepository()
    wallet_repository = FakeWalletRepository()
    transaction_manager = FakeTransactionManager()
    market_use_cases = create_market_use_cases(
        market_repository,
        bet_repository,
        position_repository,
        wallet_repository,
        transaction_manager,
    )
    user_id = uuid4()
    await wallet_repository.save(
        Wallet(id=uuid4(), user_id=user_id, balance=Decimal("1000"))
    )
    market = await market_use_cases.create_market(
        CreateMarketDTO(
            event_id=uuid4(),
            title="Coach exit",
            description="Coach can leave the club.",
            initial_probability=0.5,
            liquidity_parameter=Decimal("1000"),
        )
    )
    bet = await market_use_cases.place_bet(
        market.id,
        PlaceBetDTO(user_id=user_id, side=MarketSide.YES, amount=Decimal("100")),
    )

    result = await market_use_cases.resolve_market(
        market.id,
        ResolveMarketDTO(outcome=MarketOutcome.YES),
    )

    wallet = await wallet_repository.get_by_user_id(user_id)
    positions = await position_repository.get_by_market(market.id)
    assert result is not None
    assert result.status == MarketStatus.RESOLVED
    assert wallet is not None
    assert wallet.balance == Decimal("900.000000") + bet.shares
    assert positions[0].realized_payout == bet.shares
