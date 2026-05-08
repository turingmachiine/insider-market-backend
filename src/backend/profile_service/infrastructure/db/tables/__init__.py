from src.backend.profile_service.infrastructure.db.tables import (
    balance_transactions_table as balance_transactions_module,
)
from src.backend.profile_service.infrastructure.db.tables import (
    user_achievements_table as user_achievements_module,
)
from src.backend.profile_service.infrastructure.db.tables.achievements_table import (
    achievements_table,
)
from src.backend.profile_service.infrastructure.db.tables.activities_table import (
    activities_table,
)
from src.backend.profile_service.infrastructure.db.tables.profiles_table import (
    profiles_table,
)
from src.backend.profile_service.infrastructure.db.tables.user_balances_table import (
    user_balances_table,
)

balance_transactions_table = balance_transactions_module.balance_transactions_table
user_achievements_table = user_achievements_module.user_achievements_table

__all__ = [
    "achievements_table",
    "activities_table",
    "balance_transactions_table",
    "profiles_table",
    "user_achievements_table",
    "user_balances_table",
]
