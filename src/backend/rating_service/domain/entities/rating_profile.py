from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from src.backend.rating_service.core.utils.datetime_utils import utc_now
from src.backend.rating_service.domain.entities.rating_event import (
    RatingEvent,
    RatingEventType,
)


class UserStatus(StrEnum):
    ROOKIE = "rookie"
    SCOUT = "scout"
    ANALYST = "analyst"
    EXPERT = "expert"
    LEGEND = "legend"


@dataclass
class RatingProfile:
    user_id: UUID
    rating: int = 1000
    xp: int = 0
    level: int = 1
    status: UserStatus = UserStatus.ROOKIE
    total_predictions: int = 0
    correct_predictions: int = 0
    current_streak: int = 0
    best_streak: int = 0
    markets_created: int = 0
    analyses_published: int = 0
    comments_posted: int = 0
    active_days: int = 0
    settled_stake: Decimal = Decimal("0")
    settled_payout: Decimal = Decimal("0")
    last_activity_date: date | None = None
    last_event_at: datetime | None = None
    last_calculated_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @property
    def accuracy(self) -> float:
        if self.total_predictions == 0:
            return 0.0
        return round(self.correct_predictions / self.total_predictions, 4)

    @property
    def roi_percent(self) -> float:
        if self.settled_stake == 0:
            return 0.0
        return round(
            float(
                (self.settled_payout - self.settled_stake) / self.settled_stake * 100
            ),
            4,
        )

    def apply_event(self, event: RatingEvent) -> None:
        base_points = self._event_points(event)
        self.xp += max(base_points, 0)
        match event.event_type:
            case RatingEventType.PREDICTION_SETTLED:
                self._apply_prediction_result(event)
            case RatingEventType.MARKET_CREATED:
                self.markets_created += 1
                self.rating += 4
            case RatingEventType.ANALYSIS_PUBLISHED:
                self.analyses_published += 1
                self.rating += 6
            case RatingEventType.COMMENT_POSTED:
                self.comments_posted += 1
                self.rating += 1
            case RatingEventType.DAILY_ACTIVE:
                self._apply_daily_activity(event)

        self.level = self._calculate_level()
        self.status = self._calculate_status()
        self.last_event_at = event.occurred_at
        self.last_calculated_at = utc_now()
        self.updated_at = utc_now()

    def _apply_prediction_result(self, event: RatingEvent) -> None:
        self.total_predictions += 1
        self.settled_stake += event.stake
        self.settled_payout += event.payout
        if event.is_successful:
            self.correct_predictions += 1
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)
            self.rating += 18 + min(self.current_streak * 2, 20)
            if event.roi_delta > 0:
                self.rating += min(int(event.roi_delta * 10), 25)
        else:
            self.current_streak = 0
            self.rating -= 8
        self.rating = max(self.rating, 100)

    def _apply_daily_activity(self, event: RatingEvent) -> None:
        activity_date = event.occurred_at.date()
        if self.last_activity_date == activity_date:
            return
        if self.last_activity_date is not None:
            days_between = (activity_date - self.last_activity_date).days
            if days_between == 1:
                self.active_days += 1
                self.rating += min(1 + self.active_days // 7, 8)
            elif days_between > 1:
                self.active_days = 1
        else:
            self.active_days = 1
        self.last_activity_date = activity_date

    @staticmethod
    def _event_points(event: RatingEvent) -> int:
        if event.points:
            return event.points
        match event.event_type:
            case RatingEventType.PREDICTION_SETTLED:
                return 35 if event.is_successful else 8
            case RatingEventType.MARKET_CREATED:
                return 20
            case RatingEventType.ANALYSIS_PUBLISHED:
                return 30
            case RatingEventType.DAILY_ACTIVE:
                return 10
            case RatingEventType.COMMENT_POSTED:
                return 3

    def _calculate_level(self) -> int:
        return max(1, min(100, self.xp // 250 + 1))

    def _calculate_status(self) -> UserStatus:
        if self.rating >= 1800 and self.level >= 25:
            return UserStatus.LEGEND
        if self.rating >= 1550 and self.level >= 15:
            return UserStatus.EXPERT
        if self.rating >= 1300 and self.level >= 8:
            return UserStatus.ANALYST
        if self.rating >= 1120 and self.level >= 3:
            return UserStatus.SCOUT
        return UserStatus.ROOKIE
