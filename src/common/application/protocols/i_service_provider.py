from typing import Protocol

from src.common.application.service_context import ServiceContext


class IServiceProvider(Protocol):
    def get_service_context(self, token: str) -> ServiceContext:
        raise NotImplementedError
