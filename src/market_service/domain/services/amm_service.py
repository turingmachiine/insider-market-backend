from dataclasses import dataclass
from decimal import Decimal

from src.market_service.core.money import quantize_coin, to_decimal
from src.market_service.domain.entities import Market, MarketSide


@dataclass(frozen=True)
class Quote:
    side: MarketSide
    amount: Decimal
    shares: Decimal
    probability_before: float
    probability_after: float
    odds_before: float
    odds_after: float
    yes_pool_after: Decimal
    no_pool_after: Decimal


class AMMService:
    min_probability = 0.01
    max_probability = 0.99

    def create_initial_pools(
        self,
        initial_probability: float,
        liquidity_parameter: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """Создает стартовые AMM-пулы из начальной вероятности события.

        Пулы хранят обратную сторону вероятности: чем выше вероятность YES,
        тем больше NO-пул относительно YES-пула. Это позволяет получить
        yes_probability = no_pool / total_pool без отдельного состояния цены.
        """
        self._validate_probability(initial_probability)
        liquidity_parameter = quantize_coin(liquidity_parameter)
        if liquidity_parameter <= 0:
            raise ValueError("Liquidity parameter must be positive")
        initial_probability_decimal = to_decimal(initial_probability)
        yes_pool = liquidity_parameter * (Decimal("1") - initial_probability_decimal)
        no_pool = liquidity_parameter * initial_probability_decimal
        return quantize_coin(yes_pool), quantize_coin(no_pool)

    @staticmethod
    def quote_buy(market: Market, side: MarketSide, amount: Decimal) -> Quote:
        """Рассчитывает покупку shares без изменения состояния рынка.

        Ставка сначала двигает вероятность выбранной стороны через
        price impact: amount / (liquidity + amount). Shares выдаются по средней
        цене между вероятностью до и после сделки, поэтому крупная ставка
        получает худшую среднюю цену и сильнее сдвигает рынок.
        """
        amount = quantize_coin(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if market.yes_pool <= 0 or market.no_pool <= 0:
            raise ValueError("Market pools must be positive")

        side_probability_before = (
            market.yes_probability if side == MarketSide.YES else market.no_probability
        )
        price_impact = float(amount / (market.liquidity_parameter + amount))
        side_probability_after = (
            side_probability_before + (1 - side_probability_before) * price_impact
        )
        average_price = (side_probability_before + side_probability_after) / 2
        shares = quantize_coin(amount / to_decimal(average_price))

        yes_probability_after = (
            side_probability_after
            if side == MarketSide.YES
            else 1 - side_probability_after
        )
        total_pool_after = market.yes_pool + market.no_pool + amount
        yes_pool_after = total_pool_after * (
            Decimal("1") - to_decimal(yes_probability_after)
        )
        no_pool_after = total_pool_after * to_decimal(yes_probability_after)

        return Quote(
            side=side,
            amount=amount,
            shares=shares,
            probability_before=side_probability_before,
            probability_after=side_probability_after,
            odds_before=1 / side_probability_before,
            odds_after=1 / side_probability_after,
            yes_pool_after=quantize_coin(yes_pool_after),
            no_pool_after=quantize_coin(no_pool_after),
        )

    @staticmethod
    def apply_quote(market: Market, quote: Quote) -> None:
        """Применяет заранее рассчитанную котировку к AMM-пулам рынка."""
        market.update_pools(
            yes_pool=quote.yes_pool_after,
            no_pool=quote.no_pool_after,
        )

    def _validate_probability(self, probability: float) -> None:
        """Проверяет, что стартовая вероятность не ломает расчет odds."""
        if not self.min_probability <= probability <= self.max_probability:
            raise ValueError(
                "Initial probability must be between "
                f"{self.min_probability} and {self.max_probability}"
            )


__all__ = ["AMMService", "Quote"]
