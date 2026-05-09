from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.common.domain.interfaces import TransactionManager
from src.rating_service.application.dto import CreateRatingEventDTO
from src.rating_service.application.mappers import RatingMapper
from src.rating_service.application.ports import ProfileBalancePort
from src.rating_service.application.usecases import RatingUseCases
from src.rating_service.domain.entities import (
    AchievementDefinition,
    RatingEvent,
    RatingEventType,
    RatingProfile,
    RewardTransaction,
    RewardTransactionStatus,
    UserAchievement,
)
from src.rating_service.domain.interfaces.repositories import (
    IAchievementRepository,
    IRatingEventRepository,
    IRatingProfileRepository,
    IRewardRepository,
)
from src.rating_service.domain.services import AchievementService


class FakeTransactionManager(TransactionManager):
    def __init__(self) -> None:
        self._in_transaction = False
        self._in_nested = False

    async def begin(self) -> None:
        self._in_transaction = True

    async def begin_nested(self) -> None:
        self._in_nested = True

    async def commit(self) -> None:
        self._in_transaction = False
        self._in_nested = False

    async def rollback(self) -> None:
        self._in_transaction = False
        self._in_nested = False

    async def flush(self) -> None:
        pass

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    @property
    def in_nested(self) -> bool:
        return self._in_nested


class FakeProfileRepository(IRatingProfileRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, RatingProfile] = {}

    async def get_by_user_id(self, user_id: UUID) -> RatingProfile | None:
        return self.items.get(user_id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[RatingProfile]:
        return list(self.items.values())[offset : offset + limit]

    async def count_all(self) -> int:
        return len(self.items)

    async def get_leaderboard(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RatingProfile]:
        items = sorted(self.items.values(), key=lambda item: item.rating, reverse=True)
        return items[offset : offset + limit]

    async def save(self, profile: RatingProfile) -> RatingProfile:
        self.items[profile.user_id] = profile
        return profile


class FakeEventRepository(IRatingEventRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, RatingEvent] = {}

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> RatingEvent | None:
        return next(
            (
                item
                for item in self.items.values()
                if item.idempotency_key == idempotency_key
            ),
            None,
        )

    async def get_unprocessed(self, limit: int = 100) -> list[RatingEvent]:
        items = [item for item in self.items.values() if item.processed_at is None]
        return items[:limit]

    async def save(self, event: RatingEvent) -> RatingEvent:
        self.items[event.id] = event
        return event


class FakeAchievementRepository(IAchievementRepository):
    def __init__(self) -> None:
        self.definitions: dict[str, AchievementDefinition] = {}
        self.user_achievements: dict[UUID, UserAchievement] = {}

    async def get_definitions(
        self,
        active_only: bool = True,
    ) -> list[AchievementDefinition]:
        definitions = list(self.definitions.values())
        if active_only:
            definitions = [item for item in definitions if item.is_active]
        return definitions

    async def get_definition(self, code: str) -> AchievementDefinition | None:
        return self.definitions.get(code.strip().lower())

    async def save_definition(
        self,
        definition: AchievementDefinition,
    ) -> AchievementDefinition:
        self.definitions[definition.code] = definition
        return definition

    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievement]:
        return [
            item for item in self.user_achievements.values() if item.user_id == user_id
        ]

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

    async def save_user_achievement(
        self,
        achievement: UserAchievement,
    ) -> UserAchievement:
        self.user_achievements[achievement.id] = achievement
        return achievement


class FakeRewardRepository(IRewardRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, RewardTransaction] = {}

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> RewardTransaction | None:
        return next(
            (
                item
                for item in self.items.values()
                if item.idempotency_key == idempotency_key
            ),
            None,
        )

    async def get_pending(self, limit: int = 100) -> list[RewardTransaction]:
        items = [
            item
            for item in self.items.values()
            if item.status
            in {RewardTransactionStatus.PENDING, RewardTransactionStatus.FAILED}
        ]
        return items[:limit]

    async def save(self, reward: RewardTransaction) -> RewardTransaction:
        self.items[reward.id] = reward
        return reward


class FakeProfileBalancePort(ProfileBalancePort):
    def __init__(self) -> None:
        self.calls: list[tuple[UUID, Decimal, str, str]] = []

    async def credit_achievement_reward(
        self,
        user_id: UUID,
        amount: Decimal,
        achievement_code: str,
        idempotency_key: str,
    ) -> None:
        self.calls.append((user_id, amount, achievement_code, idempotency_key))


def create_use_cases(
    balance_port: FakeProfileBalancePort | None = None,
) -> tuple[RatingUseCases, FakeRewardRepository, FakeProfileBalancePort]:
    reward_repository = FakeRewardRepository()
    port = balance_port or FakeProfileBalancePort()
    use_cases = RatingUseCases(
        profile_repository=FakeProfileRepository(),
        event_repository=FakeEventRepository(),
        achievement_repository=FakeAchievementRepository(),
        reward_repository=reward_repository,
        achievement_service=AchievementService(),
        profile_balance_port=port,
        mapper=RatingMapper(),
        transaction_manager=FakeTransactionManager(),
    )
    return use_cases, reward_repository, port


@pytest.mark.asyncio
async def test_record_event_awards_first_prediction_and_pending_reward() -> None:
    use_cases, reward_repository, _ = create_use_cases()
    user_id = uuid4()

    event = await use_cases.record_event(
        CreateRatingEventDTO(
            user_id=user_id,
            event_type=RatingEventType.PREDICTION_SETTLED,
            is_successful=True,
            stake=Decimal("100"),
            payout=Decimal("160"),
            idempotency_key="event-1",
        )
    )

    profile = await use_cases.get_profile(user_id)
    achievements = await use_cases.get_user_achievements(user_id)
    pending_rewards = await reward_repository.get_pending()
    assert event.processed_at is not None
    assert profile is not None
    assert profile.total_predictions == 1
    assert achievements[0].achievement_code == "first_prediction"
    assert pending_rewards[0].achievement_code == "first_prediction"


@pytest.mark.asyncio
async def test_record_event_is_idempotent() -> None:
    use_cases, _, _ = create_use_cases()
    user_id = uuid4()
    dto = CreateRatingEventDTO(
        user_id=user_id,
        event_type=RatingEventType.DAILY_ACTIVE,
        idempotency_key="daily-1",
    )

    first = await use_cases.record_event(dto)
    second = await use_cases.record_event(dto)

    profile = await use_cases.get_profile(user_id)
    assert first.id == second.id
    assert profile is not None
    assert profile.active_days == 1


@pytest.mark.asyncio
async def test_dispatch_pending_rewards_marks_sent() -> None:
    use_cases, reward_repository, port = create_use_cases()
    user_id = uuid4()
    reward = RewardTransaction(
        id=uuid4(),
        user_id=user_id,
        achievement_code="first_prediction",
        amount=Decimal("25"),
    )
    await reward_repository.save(reward)

    result = await use_cases.dispatch_pending_rewards()

    assert result.rewards_dispatched == 1
    assert reward.status == RewardTransactionStatus.SENT
    assert port.calls[0][0] == user_id
