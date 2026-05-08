from src.backend.rating_service.application.dto import (
    AchievementDefinitionDTO,
    RatingEventDTO,
    RatingProfileDTO,
    RewardTransactionDTO,
    UserAchievementDTO,
)
from src.backend.rating_service.domain.entities import (
    AchievementDefinition,
    RatingEvent,
    RatingProfile,
    RewardTransaction,
    UserAchievement,
)


class RatingMapper:
    def profile_to_dto(self, profile: RatingProfile) -> RatingProfileDTO:
        return RatingProfileDTO(
            user_id=profile.user_id,
            rating=profile.rating,
            xp=profile.xp,
            level=profile.level,
            status=profile.status,
            total_predictions=profile.total_predictions,
            correct_predictions=profile.correct_predictions,
            accuracy=profile.accuracy,
            current_streak=profile.current_streak,
            best_streak=profile.best_streak,
            markets_created=profile.markets_created,
            analyses_published=profile.analyses_published,
            comments_posted=profile.comments_posted,
            active_days=profile.active_days,
            roi_percent=profile.roi_percent,
            last_event_at=profile.last_event_at,
            updated_at=profile.updated_at,
        )

    def event_to_dto(self, event: RatingEvent) -> RatingEventDTO:
        return RatingEventDTO(
            id=event.id,
            user_id=event.user_id,
            event_type=event.event_type,
            points=event.points,
            is_successful=event.is_successful,
            stake=event.stake,
            payout=event.payout,
            metadata=event.metadata,
            idempotency_key=event.idempotency_key,
            occurred_at=event.occurred_at,
            processed_at=event.processed_at,
            created_at=event.created_at,
        )

    def definition_to_dto(
        self,
        definition: AchievementDefinition,
    ) -> AchievementDefinitionDTO:
        return AchievementDefinitionDTO(
            code=definition.code,
            name=definition.name,
            description=definition.description,
            metric=definition.metric,
            threshold=definition.threshold,
            reward_amount=definition.reward_amount,
            rarity=definition.rarity,
            is_active=definition.is_active,
            created_at=definition.created_at,
        )

    def user_achievement_to_dto(
        self,
        user_achievement: UserAchievement,
        definition: AchievementDefinition | None = None,
    ) -> UserAchievementDTO:
        achievement = None
        if definition is not None:
            achievement = self.definition_to_dto(definition)
        return UserAchievementDTO(
            id=user_achievement.id,
            user_id=user_achievement.user_id,
            achievement_code=user_achievement.achievement_code,
            reward_amount=user_achievement.reward_amount,
            awarded_at=user_achievement.awarded_at,
            achievement=achievement,
        )

    def reward_to_dto(self, reward: RewardTransaction) -> RewardTransactionDTO:
        return RewardTransactionDTO(
            id=reward.id,
            user_id=reward.user_id,
            achievement_code=reward.achievement_code,
            amount=reward.amount,
            status=reward.status,
            idempotency_key=reward.idempotency_key,
            attempts=reward.attempts,
            last_error=reward.last_error,
            sent_at=reward.sent_at,
            created_at=reward.created_at,
            updated_at=reward.updated_at,
        )
