from dishka.integrations.taskiq import FromDishka, inject

from src.rating_service.application.usecases import RatingUseCases
from src.rating_service.core.config import get_settings
from src.rating_service.infrastructure.taskiq.broker import broker

settings = get_settings()


@broker.task
@inject(patch_module=True)
async def process_rating_events_task(
    use_cases: FromDishka[RatingUseCases],
) -> dict[str, int]:
    result = await use_cases.process_pending_events(
        limit=settings.BACKGROUND_BATCH_SIZE,
    )
    return {
        "events_processed": result.events_processed,
        "achievements_awarded": result.achievements_awarded,
        "rewards_dispatched": result.rewards_dispatched,
    }


@broker.task
@inject(patch_module=True)
async def dispatch_rating_rewards_task(
    use_cases: FromDishka[RatingUseCases],
) -> dict[str, int]:
    result = await use_cases.dispatch_pending_rewards(
        limit=settings.BACKGROUND_BATCH_SIZE,
    )
    return {
        "events_processed": result.events_processed,
        "achievements_awarded": result.achievements_awarded,
        "rewards_dispatched": result.rewards_dispatched,
    }
