from decimal import Decimal
from uuid import uuid4

from src.backend.rating_service.domain.entities import (
    RatingEvent,
    RatingEventType,
    RatingProfile,
    UserStatus,
)


def test_successful_prediction_increases_rating_and_streak() -> None:
    profile = RatingProfile(user_id=uuid4())
    event = RatingEvent(
        id=uuid4(),
        user_id=profile.user_id,
        event_type=RatingEventType.PREDICTION_SETTLED,
        is_successful=True,
        stake=Decimal("100"),
        payout=Decimal("180"),
    )

    profile.apply_event(event)

    assert profile.total_predictions == 1
    assert profile.correct_predictions == 1
    assert profile.current_streak == 1
    assert profile.best_streak == 1
    assert profile.rating > 1000
    assert profile.xp == 35


def test_status_moves_with_rating_and_level() -> None:
    profile = RatingProfile(user_id=uuid4(), rating=1294, xp=1750)
    event = RatingEvent(
        id=uuid4(),
        user_id=profile.user_id,
        event_type=RatingEventType.ANALYSIS_PUBLISHED,
    )

    profile.apply_event(event)

    assert profile.level >= 8
    assert profile.status == UserStatus.ANALYST
