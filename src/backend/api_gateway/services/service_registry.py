from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urljoin

from src.backend.api_gateway.config import GatewaySettings


class ServiceName(StrEnum):
    AUTH = "auth"
    NSI = "nsi"
    RUMOR = "rumor"
    EVENT = "event"
    MARKET = "market"
    NOTIFICATION = "notification"
    PROFILE = "profile"
    RATING = "rating"


@dataclass(frozen=True)
class UpstreamService:
    name: ServiceName
    base_url: str
    cache_get: bool = False
    invalidate_on_mutation: bool = False

    def build_url(self, target_path: str, query_string: str = "") -> str:
        path = f"/{target_path}" if target_path else "/"
        url = urljoin(f"{self.base_url.rstrip('/')}/", path.lstrip("/"))
        if query_string:
            return f"{url}?{query_string}"
        return url


class ServiceRegistry:
    def __init__(self, settings: GatewaySettings) -> None:
        self._services = {
            ServiceName.AUTH: UpstreamService(
                name=ServiceName.AUTH,
                base_url=str(settings.SERVICE_AUTH_URL),
            ),
            ServiceName.NSI: UpstreamService(
                name=ServiceName.NSI,
                base_url=str(settings.SERVICE_NSI_URL),
                cache_get=True,
                invalidate_on_mutation=True,
            ),
            ServiceName.RUMOR: UpstreamService(
                name=ServiceName.RUMOR,
                base_url=str(settings.SERVICE_RUMOR_URL),
                cache_get=True,
                invalidate_on_mutation=True,
            ),
            ServiceName.EVENT: UpstreamService(
                name=ServiceName.EVENT,
                base_url=str(settings.SERVICE_EVENT_URL),
                cache_get=True,
                invalidate_on_mutation=True,
            ),
            ServiceName.MARKET: UpstreamService(
                name=ServiceName.MARKET,
                base_url=str(settings.SERVICE_MARKET_URL),
                cache_get=True,
                invalidate_on_mutation=True,
            ),
            ServiceName.NOTIFICATION: UpstreamService(
                name=ServiceName.NOTIFICATION,
                base_url=str(settings.SERVICE_NOTIFICATION_URL),
            ),
            ServiceName.PROFILE: UpstreamService(
                name=ServiceName.PROFILE,
                base_url=str(settings.SERVICE_PROFILE_URL),
                cache_get=True,
                invalidate_on_mutation=True,
            ),
            ServiceName.RATING: UpstreamService(
                name=ServiceName.RATING,
                base_url=str(settings.SERVICE_RATING_URL),
                cache_get=True,
                invalidate_on_mutation=True,
            ),
        }

    def get(self, service_name: ServiceName | str) -> UpstreamService:
        return self._services[ServiceName(service_name)]
