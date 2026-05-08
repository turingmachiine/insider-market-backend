from decimal import ROUND_HALF_UP, Decimal

COIN_QUANT = Decimal("0.000001")


def to_decimal(value: Decimal | int | float | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def quantize_coin(value: Decimal | int | float | str) -> Decimal:
    return to_decimal(value).quantize(COIN_QUANT, rounding=ROUND_HALF_UP)


__all__ = ["COIN_QUANT", "quantize_coin", "to_decimal"]
