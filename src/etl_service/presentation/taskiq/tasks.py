from dishka.integrations.taskiq import FromDishka, inject

from src.etl_service.application.usecases import (
    ImportRawPublicationsUseCase,
    NormalizeRumorsUseCase,
)
from src.etl_service.core.config import get_settings
from src.etl_service.infrastructure.taskiq.broker import broker

settings = get_settings()


@broker.task(
    schedule=[
        {
            "cron": settings.RAW_IMPORT_CRON,
            "schedule_id": "import_raw_publications",
        }
    ],
)
@inject(patch_module=True)
async def import_raw_publications_task(
    use_case: FromDishka[ImportRawPublicationsUseCase],
) -> dict[str, int]:
    result = await use_case.execute()
    return {
        "sources_seen": result.sources_seen,
        "publications_seen": result.publications_seen,
        "publications_created": result.publications_created,
        "publications_skipped": result.publications_skipped,
    }


@broker.task(
    schedule=[
        {
            "cron": settings.RUMOR_NORMALIZATION_CRON,
            "schedule_id": "normalize_rumors",
        }
    ],
)
@inject(patch_module=True)
async def normalize_rumors_task(
    use_case: FromDishka[NormalizeRumorsUseCase],
) -> dict[str, int]:
    result = await use_case.execute()
    return {
        "sources_seen": result.sources_seen,
        "publications_seen": result.publications_seen,
        "rumors_created": result.rumors_created,
        "publications_skipped": result.publications_skipped,
    }
