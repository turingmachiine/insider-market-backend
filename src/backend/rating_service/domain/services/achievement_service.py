from decimal import Decimal

from src.backend.rating_service.domain.entities import (
    AchievementDefinition,
    AchievementRarity,
    RatingProfile,
)


class AchievementService:
    def default_definitions(self) -> list[AchievementDefinition]:
        return [
            AchievementDefinition(
                code="first_prediction",
                name="First Prediction",
                description="Get the first settled prediction.",
                metric="total_predictions",
                threshold=1,
                reward_amount=Decimal("25"),
            ),
            AchievementDefinition(
                code="hat_trick",
                name="Hat Trick",
                description="Build a 3 prediction winning streak.",
                metric="best_streak",
                threshold=3,
                reward_amount=Decimal("75"),
                rarity=AchievementRarity.RARE,
            ),
            AchievementDefinition(
                code="sharp_eye",
                name="Sharp Eye",
                description="Reach 10 correct predictions.",
                metric="correct_predictions",
                threshold=10,
                reward_amount=Decimal("150"),
                rarity=AchievementRarity.RARE,
            ),
            AchievementDefinition(
                code="market_maker",
                name="Market Maker",
                description="Create 5 markets.",
                metric="markets_created",
                threshold=5,
                reward_amount=Decimal("120"),
                rarity=AchievementRarity.RARE,
            ),
            AchievementDefinition(
                code="tactician",
                name="Tactician",
                description="Publish 5 analyses.",
                metric="analyses_published",
                threshold=5,
                reward_amount=Decimal("100"),
                rarity=AchievementRarity.RARE,
            ),
            AchievementDefinition(
                code="scout_status",
                name="Scout Status",
                description="Reach Scout user status.",
                metric="status_rank",
                threshold=2,
                reward_amount=Decimal("100"),
                rarity=AchievementRarity.RARE,
            ),
            AchievementDefinition(
                code="expert_status",
                name="Expert Status",
                description="Reach Expert user status.",
                metric="status_rank",
                threshold=4,
                reward_amount=Decimal("500"),
                rarity=AchievementRarity.EPIC,
            ),
            AchievementDefinition(
                code="legend_status",
                name="Legend Status",
                description="Reach Legend user status.",
                metric="status_rank",
                threshold=5,
                reward_amount=Decimal("1500"),
                rarity=AchievementRarity.LEGENDARY,
            ),
            AchievementDefinition(
                code="regular",
                name="Regular",
                description="Be active for 7 days.",
                metric="active_days",
                threshold=7,
                reward_amount=Decimal("80"),
            ),
        ]

    def evaluate(
        self,
        profile: RatingProfile,
        definitions: list[AchievementDefinition],
        awarded_codes: set[str],
    ) -> list[AchievementDefinition]:
        result: list[AchievementDefinition] = []
        for definition in definitions:
            if not definition.is_active or definition.code in awarded_codes:
                continue
            if self._metric_value(profile, definition.metric) >= definition.threshold:
                result.append(definition)
        return result

    @staticmethod
    def _metric_value(profile: RatingProfile, metric: str) -> int:
        if metric == "status_rank":
            ranks = {
                "rookie": 1,
                "scout": 2,
                "analyst": 3,
                "expert": 4,
                "legend": 5,
            }
            return ranks[profile.status.value]
        value = getattr(profile, metric)
        if isinstance(value, float):
            return int(value)
        return int(value)
