from decimal import ROUND_HALF_UP, Decimal

COIN_SCALE = Decimal("0.000001")


def quantize_coin(value: Decimal) -> Decimal:
    return value.quantize(COIN_SCALE, rounding=ROUND_HALF_UP)
