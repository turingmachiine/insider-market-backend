import pytest

from src.etl_service.application.usecases import (
    ImportRawPublicationsUseCase,
    NormalizeRumorsUseCase,
)
from src.etl_service.core.config import ETLSettings
from src.etl_service.infrastructure.di.container_factory import create_container


@pytest.mark.asyncio
async def test_container_resolves_etl_use_cases() -> None:
    settings = ETLSettings(
        RUMOR_SERVICE_URL="http://rumor.test",
        SOURCE_FETCH_LIMIT=1,
        RAW_PUBLICATIONS_LIMIT=2,
        EXISTING_RUMORS_LIMIT=3,
    )
    container = create_container(settings)
    try:
        async with container() as request_container:
            import_use_case = await request_container.get(ImportRawPublicationsUseCase)
            normalize_use_case = await request_container.get(NormalizeRumorsUseCase)

            assert import_use_case.existing_publications_limit == 2
            assert normalize_use_case.raw_publications_limit == 2
            assert normalize_use_case.existing_rumors_limit == 3
    finally:
        await container.close()
