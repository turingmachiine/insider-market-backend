from uuid import UUID, uuid4

from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager
from src.rating_service.application.dto import (
    AchievementDefinitionDTO,
    CreateAchievementDefinitionDTO,
    CreateRatingEventDTO,
    RatingEventDTO,
    RatingProfileDTO,
    RatingRecalculationDTO,
    RewardTransactionDTO,
    UserAchievementDTO,
)
from src.rating_service.application.mappers import RatingMapper
from src.rating_service.application.ports import ProfileBalancePort
from src.rating_service.domain.entities import (
    AchievementDefinition,
    RatingEvent,
    RatingProfile,
    RewardTransaction,
    UserAchievement,
)
from src.rating_service.domain.interfaces.repositories import (
    IAchievementRepository,
    IRatingEventRepository,
    IRatingProfileRepository,
    IRewardRepository,
)
from src.rating_service.domain.services import AchievementService


@use_case
class RatingUseCases(HasTransactionManager):
    profile_repository: IRatingProfileRepository
    event_repository: IRatingEventRepository
    achievement_repository: IAchievementRepository
    reward_repository: IRewardRepository
    achievement_service: AchievementService
    profile_balance_port: ProfileBalancePort
    mapper: RatingMapper
    transaction_manager: TransactionManager

    async def get_profile(self, user_id: UUID) -> RatingProfileDTO | None:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            return None
        return self.mapper.profile_to_dto(profile)

    async def get_profiles(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RatingProfileDTO]:
        profiles = await self.profile_repository.get_all(limit=limit, offset=offset)
        return [self.mapper.profile_to_dto(item) for item in profiles]

    async def count_profiles(self) -> int:
        return await self.profile_repository.count_all()

    async def get_leaderboard(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RatingProfileDTO]:
        profiles = await self.profile_repository.get_leaderboard(
            limit=limit,
            offset=offset,
        )
        return [self.mapper.profile_to_dto(item) for item in profiles]

    @transactional()
    async def record_event(self, dto: CreateRatingEventDTO) -> RatingEventDTO:
        if dto.idempotency_key is not None:
            existing = await self.event_repository.get_by_idempotency_key(
                dto.idempotency_key
            )
            if existing is not None:
                return self.mapper.event_to_dto(existing)
        if dto.occurred_at is None:
            event = RatingEvent(
                id=uuid4(),
                user_id=dto.user_id,
                event_type=dto.event_type,
                points=dto.points,
                is_successful=dto.is_successful,
                stake=dto.stake,
                payout=dto.payout,
                metadata=dto.metadata,
                idempotency_key=dto.idempotency_key,
            )
        else:
            event = RatingEvent(
                id=uuid4(),
                user_id=dto.user_id,
                event_type=dto.event_type,
                points=dto.points,
                is_successful=dto.is_successful,
                stake=dto.stake,
                payout=dto.payout,
                metadata=dto.metadata,
                idempotency_key=dto.idempotency_key,
                occurred_at=dto.occurred_at,
            )
        await self._apply_event(event)
        saved = await self.event_repository.save(event)
        return self.mapper.event_to_dto(saved)

    @transactional()
    async def process_pending_events(self, limit: int = 100) -> RatingRecalculationDTO:
        events = await self.event_repository.get_unprocessed(limit=limit)
        achievements_awarded = 0
        for event in events:
            achievements_awarded += await self._apply_event(event)
            await self.event_repository.save(event)
        return RatingRecalculationDTO(
            events_processed=len(events),
            achievements_awarded=achievements_awarded,
            rewards_dispatched=0,
        )

    @transactional()
    async def recalculate_user(self, user_id: UUID) -> RatingProfileDTO:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if profile is None:
            profile = RatingProfile(user_id=user_id)
            await self.profile_repository.save(profile)
        definitions = await self._ensure_default_achievements()
        awarded = await self.achievement_repository.get_user_achievements(user_id)
        newly_awarded = self.achievement_service.evaluate(
            profile=profile,
            definitions=definitions,
            awarded_codes={item.achievement_code for item in awarded},
        )
        for definition in newly_awarded:
            await self._award_achievement(profile, definition)
        await self.profile_repository.save(profile)
        return self.mapper.profile_to_dto(profile)

    async def get_achievement_definitions(self) -> list[AchievementDefinitionDTO]:
        definitions = await self._ensure_default_achievements()
        return [self.mapper.definition_to_dto(item) for item in definitions]

    @transactional()
    async def create_achievement_definition(
        self,
        dto: CreateAchievementDefinitionDTO,
    ) -> AchievementDefinitionDTO:
        existing = await self.achievement_repository.get_definition(dto.code)
        if existing is not None:
            raise ValueError(f"Achievement {dto.code} already exists")
        definition = AchievementDefinition(**dto.__dict__)
        saved = await self.achievement_repository.save_definition(definition)
        return self.mapper.definition_to_dto(saved)

    async def get_user_achievements(self, user_id: UUID) -> list[UserAchievementDTO]:
        achievements = await self.achievement_repository.get_user_achievements(user_id)
        result: list[UserAchievementDTO] = []
        for achievement in achievements:
            definition = await self.achievement_repository.get_definition(
                achievement.achievement_code
            )
            result.append(self.mapper.user_achievement_to_dto(achievement, definition))
        return result

    @transactional()
    async def dispatch_pending_rewards(
        self, limit: int = 100
    ) -> RatingRecalculationDTO:
        rewards = await self.reward_repository.get_pending(limit=limit)
        sent = 0
        for reward in rewards:
            try:
                await self.profile_balance_port.credit_achievement_reward(
                    user_id=reward.user_id,
                    amount=reward.amount,
                    achievement_code=reward.achievement_code,
                    idempotency_key=reward.idempotency_key or str(reward.id),
                )
            except Exception as exc:
                reward.mark_failed(str(exc))
            else:
                reward.mark_sent()
                sent += 1
            await self.reward_repository.save(reward)
        return RatingRecalculationDTO(
            events_processed=0,
            achievements_awarded=0,
            rewards_dispatched=sent,
        )

    async def get_pending_rewards(self, limit: int = 100) -> list[RewardTransactionDTO]:
        rewards = await self.reward_repository.get_pending(limit=limit)
        return [self.mapper.reward_to_dto(item) for item in rewards]

    async def _apply_event(self, event: RatingEvent) -> int:
        profile = await self.profile_repository.get_by_user_id(event.user_id)
        if profile is None:
            profile = RatingProfile(user_id=event.user_id)
        profile.apply_event(event)
        event.mark_processed()
        await self.profile_repository.save(profile)
        definitions = await self._ensure_default_achievements()
        awarded = await self.achievement_repository.get_user_achievements(event.user_id)
        new_definitions = self.achievement_service.evaluate(
            profile=profile,
            definitions=definitions,
            awarded_codes={item.achievement_code for item in awarded},
        )
        for definition in new_definitions:
            await self._award_achievement(profile, definition)
        return len(new_definitions)

    async def _award_achievement(
        self,
        profile: RatingProfile,
        definition: AchievementDefinition,
    ) -> None:
        existing = await self.achievement_repository.get_user_achievement(
            user_id=profile.user_id,
            achievement_code=definition.code,
        )
        if existing is not None:
            return
        achievement = UserAchievement(
            id=uuid4(),
            user_id=profile.user_id,
            achievement_code=definition.code,
            reward_amount=definition.reward_amount,
        )
        await self.achievement_repository.save_user_achievement(achievement)
        reward = RewardTransaction(
            id=uuid4(),
            user_id=profile.user_id,
            achievement_code=definition.code,
            amount=definition.reward_amount,
        )
        existing_reward = await self.reward_repository.get_by_idempotency_key(
            reward.idempotency_key or str(reward.id)
        )
        if existing_reward is None and reward.amount > 0:
            await self.reward_repository.save(reward)

    async def _ensure_default_achievements(self) -> list[AchievementDefinition]:
        definitions = await self.achievement_repository.get_definitions(
            active_only=False
        )
        existing_codes = {item.code for item in definitions}
        for definition in self.achievement_service.default_definitions():
            if definition.code not in existing_codes:
                definitions.append(
                    await self.achievement_repository.save_definition(definition)
                )
        return [item for item in definitions if item.is_active]
