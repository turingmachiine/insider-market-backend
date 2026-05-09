from decimal import Decimal
from uuid import uuid4

import pytest

from src.market_service.domain.entities import Market, MarketSide
from src.market_service.domain.services import AMMService


def test_initial_probability_defines_initial_odds() -> None:
    service = AMMService()
    yes_pool, no_pool = service.create_initial_pools(
        initial_probability=0.25,
        liquidity_parameter=Decimal("1000"),
    )
    market = Market(
        id=uuid4(),
        event_id=uuid4(),
        title="Transfer",
        description="Player can join the club.",
        initial_probability=0.25,
        liquidity_parameter=Decimal("1000"),
        yes_pool=yes_pool,
        no_pool=no_pool,
    )

    assert market.yes_probability == pytest.approx(0.25)
    assert market.no_probability == pytest.approx(0.75)
    assert market.yes_odds == pytest.approx(4.0)


def test_yes_buy_moves_probability_up() -> None:
    service = AMMService()
    yes_pool, no_pool = service.create_initial_pools(
        initial_probability=0.5,
        liquidity_parameter=Decimal("1000"),
    )
    market = Market(
        id=uuid4(),
        event_id=uuid4(),
        title="Coach exit",
        description="Coach can leave the club.",
        initial_probability=0.5,
        liquidity_parameter=Decimal("1000"),
        yes_pool=yes_pool,
        no_pool=no_pool,
    )

    quote = service.quote_buy(market, MarketSide.YES, Decimal("100"))
    service.apply_quote(market, quote)

    assert quote.shares > Decimal("100")
    assert market.yes_probability > 0.5
    assert market.yes_odds < 2.0
