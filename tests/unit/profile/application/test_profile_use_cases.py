from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.common.domain.interfaces import TransactionManager
from src.profile_service.application.dto import (
    AwardAchievementDTO,
    BalanceOperationDTO,
    CreateAchievementDTO,
    CreateProfileDTO,
)
from src.profile_service.application.mappers import (
    AchievementMapper,
    ActivityMapper,
    BalanceMapper,
    ProfileMapper,
)
from src.profile_service.application.usecases import ProfileUseCases
from src.profile_service.domain.entities import (
    Achievement,
    Activity,
    ActivityType,
    BalanceTransaction,
    BalanceTransactionType,
    Profile,
    UserAchievement,
    UserBalance,
)
from src.profile_service.domain.interfaces.repositories import (
    IAchievementRepository,
    IActivityRepository,
    IBalanceRepository,
    IProfileRepository,
)


class FakeTransactionManager(TransactionManager):
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
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
        """fake repository"""
        pass

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    @property
    def in_nested(self) -> bool:
        return self._in_nested


class FakeProfileRepository(IProfileRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Profile] = {}

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        return next(
            (item for item in self.items.values() if item.user_id == user_id), None
        )

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Profile]:
        return list(self.items.values())[offset : offset + limit]

    async def count_all(self) -> int:
        return len(self.items)

    async def save(self, profile: Profile) -> Profile:
        self.items[profile.id] = profile
        return profile


class FakeBalanceRepository(IBalanceRepository):
    def __init__(self) -> None:
        self.balances: dict[UUID, UserBalance] = {}
        self.transactions: dict[UUID, BalanceTransaction] = {}

    async def get_by_user_id(self, user_id: UUID) -> UserBalance | None:
        return next(
            (item for item in self.balances.values() if item.user_id == user_id),
            None,
        )

    async def save(self, balance: UserBalance) -> UserBalance:
        self.balances[balance.id] = balance
        return balance

    async def save_transaction(
        self,
        transaction: BalanceTransaction,
    ) -> BalanceTransaction:
        self.transactions[transaction.id] = transaction
        return transaction

    async def get_transactions(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BalanceTransaction]:
        items = [item for item in self.transactions.values() if item.user_id == user_id]
        return items[offset : offset + limit]

    async def get_transaction_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> BalanceTransaction | None:
        return next(
            (
                item
                for item in self.transactions.values()
                if item.idempotency_key == idempotency_key
            ),
            None,
        )


class FakeActivityRepository(IActivityRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Activity] = {}

    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        activity_type: ActivityType | None = None,
    ) -> list[Activity]:
        items = [item for item in self.items.values() if item.user_id == user_id]
        if activity_type is not None:
            items = [item for item in items if item.activity_type == activity_type]
        return items[offset : offset + limit]

    async def save(self, activity: Activity) -> Activity:
        self.items[activity.id] = activity
        return activity


class FakeAchievementRepository(IAchievementRepository):
    def __init__(self) -> None:
        self.achievements: dict[str, Achievement] = {}
        self.user_achievements: dict[UUID, UserAchievement] = {}

    async def get_achievement(self, code: str) -> Achievement | None:
        return self.achievements.get(code.strip().lower())

    async def get_achievements(self) -> list[Achievement]:
        return list(self.achievements.values())

    async def save_achievement(self, achievement: Achievement) -> Achievement:
        self.achievements[achievement.code] = achievement
        return achievement

    async def get_user_achievement(
        self,
        user_id: UUID,
        achievement_code: str,
    ) -> UserAchievement | None:
        return next(
            (
                item
                for item in self.user_achievements.values()
                if item.user_id == user_id
                and item.achievement_code == achievement_code.strip().lower()
            ),
            None,
        )

    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievement]:
        return [
            item for item in self.user_achievements.values() if item.user_id == user_id
        ]

    async def save_user_achievement(
        self,
        user_achievement: UserAchievement,
    ) -> UserAchievement:
        self.user_achievements[user_achievement.id] = user_achievement
        return user_achievement


def create_use_cases(
    profile_repository: FakeProfileRepository,
    balance_repository: FakeBalanceRepository,
    activity_repository: FakeActivityRepository,
    achievement_repository: FakeAchievementRepository,
    transaction_manager: FakeTransactionManager,
) -> ProfileUseCases:
    return ProfileUseCases(
        profile_repository=profile_repository,
        balance_repository=balance_repository,
        activity_repository=activity_repository,
        achievement_repository=achievement_repository,
        profile_mapper=ProfileMapper(),
        balance_mapper=BalanceMapper(),
        activity_mapper=ActivityMapper(),
        achievement_mapper=AchievementMapper(),
        transaction_manager=transaction_manager,
    )


@pytest.mark.asyncio
async def test_create_profile_creates_balance_and_activity() -> None:
    use_cases = create_use_cases(
        FakeProfileRepository(),
        FakeBalanceRepository(),
        FakeActivityRepository(),
        FakeAchievementRepository(),
        FakeTransactionManager(),
    )
    user_id = uuid4()

    profile = await use_cases.create_profile(
        CreateProfileDTO(
            user_id=user_id,
            display_name="Scout",
            initial_balance=Decimal("1500"),
        )
    )

    activity = await use_cases.get_activity(user_id)
    transactions = await use_cases.get_balance_transactions(user_id)
    assert profile.balance == Decimal("1500.000000")
    assert profile.available_balance == Decimal("1500.000000")
    assert activity[0].activity_type == ActivityType.PROFILE_CREATED
    assert transactions[0].transaction_type == BalanceTransactionType.CREDIT


@pytest.mark.asyncio
async def test_public_profile_only_returns_public_profiles() -> None:
    use_cases = create_use_cases(
        FakeProfileRepository(),
        FakeBalanceRepository(),
        FakeActivityRepository(),
        FakeAchievementRepository(),
        FakeTransactionManager(),
    )
    public_user_id = uuid4()
    private_user_id = uuid4()
    await use_cases.create_profile(
        CreateProfileDTO(
            user_id=public_user_id,
            display_name="Public Trader",
            is_public=True,
        )
    )
    await use_cases.create_profile(
        CreateProfileDTO(user_id=private_user_id, display_name="Private Trader")
    )

    public_profile = await use_cases.get_public_profile(public_user_id)
    private_profile = await use_cases.get_public_profile(private_user_id)

    assert public_profile is not None
    assert public_profile.user_id == public_user_id
    assert private_profile is None


@pytest.mark.asyncio
async def test_balance_reserve_operation_is_idempotent() -> None:
    profile_repository = FakeProfileRepository()
    balance_repository = FakeBalanceRepository()
    use_cases = create_use_cases(
        profile_repository,
        balance_repository,
        FakeActivityRepository(),
        FakeAchievementRepository(),
        FakeTransactionManager(),
    )
    user_id = uuid4()
    await use_cases.create_profile(
        CreateProfileDTO(user_id=user_id, display_name="Trader")
    )

    operation = BalanceOperationDTO(
        transaction_type=BalanceTransactionType.RESERVE,
        amount=Decimal("100"),
        source="market.bet",
        idempotency_key="bet-1",
    )
    first = await use_cases.apply_balance_operation(user_id, operation)
    second = await use_cases.apply_balance_operation(user_id, operation)

    balance = await balance_repository.get_by_user_id(user_id)
    assert first is not None
    assert second is not None
    assert first.id == second.id
    assert balance is not None
    assert balance.balance == Decimal("1000.000000")
    assert balance.reserved_balance == Decimal("100.000000")


@pytest.mark.asyncio
async def test_award_achievement_adds_profile_activity() -> None:
    use_cases = create_use_cases(
        FakeProfileRepository(),
        FakeBalanceRepository(),
        FakeActivityRepository(),
        FakeAchievementRepository(),
        FakeTransactionManager(),
    )
    user_id = uuid4()
    await use_cases.create_profile(
        CreateProfileDTO(user_id=user_id, display_name="Analyst")
    )
    await use_cases.create_achievement(
        CreateAchievementDTO(
            code="first_win",
            name="First Win",
            description="Resolved a first winning market.",
        )
    )

    achievement = await use_cases.award_achievement(
        user_id,
        AwardAchievementDTO(achievement_code="first_win"),
    )

    activity = await use_cases.get_activity(
        user_id,
        activity_type=ActivityType.ACHIEVEMENT_AWARDED,
    )
    assert achievement is not None
    assert achievement.achievement_code == "first_win"
    assert activity[0].activity_type == ActivityType.ACHIEVEMENT_AWARDED
