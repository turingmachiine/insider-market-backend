from decimal import Decimal
from uuid import uuid4

import pytest

from src.profile_service.domain.entities import UserBalance


def test_balance_reserve_and_release_updates_available_balance() -> None:
    balance = UserBalance(id=uuid4(), user_id=uuid4(), balance=Decimal("1000"))

    balance.reserve(Decimal("250"))
    assert balance.balance == Decimal("1000.000000")
    assert balance.reserved_balance == Decimal("250.000000")
    assert balance.available_balance == Decimal("750.000000")

    balance.release(Decimal("100"))
    assert balance.reserved_balance == Decimal("150.000000")
    assert balance.available_balance == Decimal("850.000000")


def test_balance_debit_requires_available_balance() -> None:
    balance = UserBalance(id=uuid4(), user_id=uuid4(), balance=Decimal("100"))
    balance.reserve(Decimal("90"))

    with pytest.raises(ValueError, match="Insufficient available balance"):
        balance.debit(Decimal("20"))
