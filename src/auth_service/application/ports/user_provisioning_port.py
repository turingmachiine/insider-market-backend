from abc import ABC, abstractmethod
from uuid import UUID


class UserProvisioningPort(ABC):
    @abstractmethod
    async def provision_user(
        self,
        user_id: UUID,
        email: str,
        correlation_id: str | None = None,
    ) -> None:
        raise NotImplementedError


__all__ = ["UserProvisioningPort"]
