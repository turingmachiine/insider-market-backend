import httpx
from dishka import Provider, Scope, provide

from src.etl_service.application.ports import (
    PublicationFetcher,
    RumorExtractor,
    RumorServicePort,
)
from src.etl_service.core.config import ETLSettings
from src.etl_service.infrastructure.clients import RumorServiceHttpClient
from src.etl_service.infrastructure.extractors import RuleBasedRumorExtractor
from src.etl_service.infrastructure.fetchers import HttpPublicationFetcher


class PortProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_rumor_service_port(
        self,
        http_client: httpx.AsyncClient,
        settings: ETLSettings,
    ) -> RumorServicePort:
        return RumorServiceHttpClient(http_client, settings)

    @provide
    def provide_publication_fetcher(
        self,
        http_client: httpx.AsyncClient,
        settings: ETLSettings,
    ) -> PublicationFetcher:
        return HttpPublicationFetcher(
            http_client,
            limit=settings.SOURCE_FETCH_LIMIT,
        )

    @provide
    def provide_rumor_extractor(self) -> RumorExtractor:
        return RuleBasedRumorExtractor()
