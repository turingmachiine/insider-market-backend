from decimal import ROUND_HALF_UP, Decimal

COIN_QUANT = Decimal("0.000001")


def quantize_coin(amount: Decimal) -> Decimal:
    return amount.quantize(COIN_QUANT, rounding=ROUND_HALF_UP)
