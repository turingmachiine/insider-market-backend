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
