from decimal import Decimal
from uuid import UUID, uuid4

from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager
from src.profile_service.application.dto import (
    AchievementDTO,
    ActivityDTO,
    AwardAchievementDTO,
    BalanceOperationDTO,
    BalanceTransactionDTO,
    CreateAchievementDTO,
    CreateActivityDTO,
    CreateProfileDTO,
    ProfileDTO,
    UpdateProfileDTO,
    UserAchievementDTO,
    UserBalanceDTO,
)
from src.profile_service.application.mappers import (
    IAchievementMapper,
    IActivityMapper,
    IBalanceMapper,
    IProfileMapper,
)
from src.profile_service.core.money import quantize_coin
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


@use_case
class ProfileUseCases(HasTransactionManager):
    profile_repository: IProfileRepository
    balance_repository: IBalanceRepository
    activity_repository: IActivityRepository
    achievement_repository: IAchievementRepository
    profile_mapper: IProfileMapper
    balance_mapper: IBalanceMapper
    activity_mapper: IActivityMapper
    achievement_mapper: IAchievementMapper
    transaction_manager: TransactionManager

    async def get_profile(self, user_id: UUID) -> ProfileDTO | None:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            return None
        balance = await self._get_or_create_balance(user_id)
        return self.profile_mapper.to_dto(profile, balance)

    async def get_profiles(self, limit: int = 100, offset: int = 0) -> list[ProfileDTO]:
        profiles = await self.profile_repository.get_all(limit=limit, offset=offset)
        result: list[ProfileDTO] = []
        for profile in profiles:
            balance = await self._get_or_create_balance(profile.user_id)
            result.append(self.profile_mapper.to_dto(profile, balance))
        return result

    async def count_profiles(self) -> int:
        return await self.profile_repository.count_all()

    @transactional()
    async def create_profile(self, dto: CreateProfileDTO) -> ProfileDTO:
        existing_profile = await self.profile_repository.get_by_user_id(dto.user_id)
        if existing_profile is not None:
            raise ValueError(f"Profile for user {str(dto.user_id)} already exists")
        if dto.initial_balance < 0:
            raise ValueError("Initial balance must not be negative")

        profile = Profile(
            id=uuid4(),
            user_id=dto.user_id,
            display_name=dto.display_name,
            bio=dto.bio,
            avatar_url=dto.avatar_url,
            favorite_club=dto.favorite_club,
        )
        balance = UserBalance(
            id=uuid4(),
            user_id=dto.user_id,
            balance=quantize_coin(dto.initial_balance),
        )
        saved_profile = await self.profile_repository.save(profile)
        saved_balance = await self.balance_repository.save(balance)
        await self.activity_repository.save(
            Activity(
                id=uuid4(),
                user_id=dto.user_id,
                activity_type=ActivityType.PROFILE_CREATED,
                title="Profile created",
            )
        )
        if dto.initial_balance > 0:
            await self.balance_repository.save_transaction(
                BalanceTransaction(
                    id=uuid4(),
                    user_id=dto.user_id,
                    transaction_type=BalanceTransactionType.CREDIT,
                    amount=dto.initial_balance,
                    balance_after=saved_balance.balance,
                    reserved_after=saved_balance.reserved_balance,
                    source="profile.initial_balance",
                )
            )
        return self.profile_mapper.to_dto(saved_profile, saved_balance)

    @transactional()
    async def update_profile(
        self,
        user_id: UUID,
        dto: UpdateProfileDTO,
    ) -> ProfileDTO | None:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            return None
        profile.update(
            display_name=dto.display_name,
            bio=dto.bio,
            avatar_url=dto.avatar_url,
            favorite_club=dto.favorite_club,
        )
        saved_profile = await self.profile_repository.save(profile)
        balance = await self._get_or_create_balance(user_id)
        await self.activity_repository.save(
            Activity(
                id=uuid4(),
                user_id=user_id,
                activity_type=ActivityType.PROFILE_UPDATED,
                title="Profile updated",
            )
        )
        return self.profile_mapper.to_dto(saved_profile, balance)

    async def get_balance(self, user_id: UUID) -> UserBalanceDTO | None:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            return None
        balance = await self._get_or_create_balance(user_id)
        return self.balance_mapper.to_dto(balance)

    async def get_balance_transactions(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BalanceTransactionDTO]:
        transactions = await self.balance_repository.get_transactions(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return [self.balance_mapper.transaction_to_dto(item) for item in transactions]

    @transactional()
    async def apply_balance_operation(
        self,
        user_id: UUID,
        dto: BalanceOperationDTO,
    ) -> BalanceTransactionDTO | None:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            return None
        if dto.idempotency_key is not None:
            existing = await self.balance_repository.get_transaction_by_idempotency_key(
                dto.idempotency_key
            )
            if existing is not None:
                return self.balance_mapper.transaction_to_dto(existing)

        balance = await self._get_or_create_balance(user_id)
        amount = quantize_coin(dto.amount)
        self._apply_balance_change(balance, dto.transaction_type, amount)
        saved_balance = await self.balance_repository.save(balance)
        transaction = BalanceTransaction(
            id=uuid4(),
            user_id=user_id,
            transaction_type=dto.transaction_type,
            amount=amount,
            balance_after=saved_balance.balance,
            reserved_after=saved_balance.reserved_balance,
            source=dto.source,
            idempotency_key=dto.idempotency_key,
            metadata=dto.metadata,
        )
        saved_transaction = await self.balance_repository.save_transaction(transaction)
        await self.activity_repository.save(
            Activity(
                id=uuid4(),
                user_id=user_id,
                activity_type=ActivityType.BALANCE_CHANGED,
                title="Balance changed",
                payload={
                    "transaction_id": str(saved_transaction.id),
                    "transaction_type": saved_transaction.transaction_type.value,
                    "amount": str(saved_transaction.amount),
                    "source": saved_transaction.source,
                },
            )
        )
        return self.balance_mapper.transaction_to_dto(saved_transaction)

    async def get_activity(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        activity_type: ActivityType | None = None,
    ) -> list[ActivityDTO]:
        activities = await self.activity_repository.get_by_user_id(
            user_id=user_id,
            limit=limit,
            offset=offset,
            activity_type=activity_type,
        )
        return [self.activity_mapper.to_dto(item) for item in activities]

    @transactional()
    async def add_activity(
        self,
        user_id: UUID,
        dto: CreateActivityDTO,
    ) -> ActivityDTO | None:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            return None
        activity = Activity(
            id=uuid4(),
            user_id=user_id,
            activity_type=dto.activity_type,
            title=dto.title,
            description=dto.description,
            payload=dto.payload,
        )
        saved_activity = await self.activity_repository.save(activity)
        return self.activity_mapper.to_dto(saved_activity)

    async def get_achievements(self) -> list[AchievementDTO]:
        achievements = await self.achievement_repository.get_achievements()
        return [self.achievement_mapper.to_dto(item) for item in achievements]

    @transactional()
    async def create_achievement(
        self,
        dto: CreateAchievementDTO,
    ) -> AchievementDTO:
        existing = await self.achievement_repository.get_achievement(dto.code)
        if existing is not None:
            raise ValueError(f"Achievement {dto.code} already exists")
        achievement = Achievement(
            code=dto.code,
            name=dto.name,
            description=dto.description,
            icon_url=dto.icon_url,
        )
        saved_achievement = await self.achievement_repository.save_achievement(
            achievement
        )
        return self.achievement_mapper.to_dto(saved_achievement)

    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievementDTO]:
        user_achievements = await self.achievement_repository.get_user_achievements(
            user_id
        )
        result: list[UserAchievementDTO] = []
        for user_achievement in user_achievements:
            achievement = await self.achievement_repository.get_achievement(
                user_achievement.achievement_code
            )
            result.append(
                self.achievement_mapper.user_to_dto(user_achievement, achievement)
            )
        return result

    @transactional()
    async def award_achievement(
        self,
        user_id: UUID,
        dto: AwardAchievementDTO,
    ) -> UserAchievementDTO | None:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            return None
        achievement = await self.achievement_repository.get_achievement(
            dto.achievement_code
        )
        if achievement is None:
            raise ValueError(f"Achievement {dto.achievement_code} not found")
        existing = await self.achievement_repository.get_user_achievement(
            user_id=user_id,
            achievement_code=dto.achievement_code,
        )
        if existing is not None:
            return self.achievement_mapper.user_to_dto(existing, achievement)
        user_achievement = UserAchievement(
            id=uuid4(),
            user_id=user_id,
            achievement_code=dto.achievement_code,
            progress=dto.progress,
        )
        saved = await self.achievement_repository.save_user_achievement(
            user_achievement
        )
        await self.activity_repository.save(
            Activity(
                id=uuid4(),
                user_id=user_id,
                activity_type=ActivityType.ACHIEVEMENT_AWARDED,
                title="Achievement awarded",
                payload={"achievement_code": achievement.code},
            )
        )
        return self.achievement_mapper.user_to_dto(saved, achievement)

    async def _get_or_create_balance(self, user_id: UUID) -> UserBalance:
        balance = await self.balance_repository.get_by_user_id(user_id)
        if balance is not None:
            return balance
        return await self.balance_repository.save(
            UserBalance(id=uuid4(), user_id=user_id, balance=Decimal("0"))
        )

    @staticmethod
    def _apply_balance_change(
        balance: UserBalance,
        transaction_type: BalanceTransactionType,
        amount: Decimal,
    ) -> None:
        match transaction_type:
            case BalanceTransactionType.CREDIT:
                balance.credit(amount)
            case BalanceTransactionType.DEBIT:
                balance.debit(amount)
            case BalanceTransactionType.RESERVE:
                balance.reserve(amount)
            case BalanceTransactionType.RELEASE:
                balance.release(amount)
