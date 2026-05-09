from dishka import Provider, Scope, provide

from src.etl_service.application.ports import (
    PublicationFetcher,
    RumorExtractor,
    RumorServicePort,
)
from src.etl_service.application.usecases import (
    ImportRawPublicationsUseCase,
    NormalizeRumorsUseCase,
)
from src.etl_service.core.config import ETLSettings


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_import_raw_publications_use_case(
        self,
        rumor_service: RumorServicePort,
        publication_fetcher: PublicationFetcher,
        settings: ETLSettings,
    ) -> ImportRawPublicationsUseCase:
        return ImportRawPublicationsUseCase(
            rumor_service=rumor_service,
            publication_fetcher=publication_fetcher,
            existing_publications_limit=settings.RAW_PUBLICATIONS_LIMIT,
        )

    @provide
    def provide_normalize_rumors_use_case(
        self,
        rumor_service: RumorServicePort,
        rumor_extractor: RumorExtractor,
        settings: ETLSettings,
    ) -> NormalizeRumorsUseCase:
        return NormalizeRumorsUseCase(
            rumor_service=rumor_service,
            rumor_extractor=rumor_extractor,
            raw_publications_limit=settings.RAW_PUBLICATIONS_LIMIT,
            existing_rumors_limit=settings.EXISTING_RUMORS_LIMIT,
        )
