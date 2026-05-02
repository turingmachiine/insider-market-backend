from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalIdentity:
    provider: str
    subject: str
    email: str


class ExternalAuthStrategy(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> ExternalIdentity:
        raise NotImplementedError


class StubExternalAuthStrategy(ExternalAuthStrategy):
    async def authenticate(self, token: str) -> ExternalIdentity:
        return ExternalIdentity(
            provider="stub",
            subject=token or "stub-subject",
            email="stub@example.com",
        )
