from abc import ABC, abstractmethod
from uuid import UUID

from src.market_service.domain.entities import AuditLog, MarketAuditAction


class IAuditLogRepository(ABC):
    @abstractmethod
    async def save(self, audit_log: AuditLog) -> AuditLog:
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        action: MarketAuditAction | None = None,
        actor_user_id: UUID | None = None,
    ) -> list[AuditLog]:
        raise NotImplementedError

    @abstractmethod
    async def count_all(
        self,
        action: MarketAuditAction | None = None,
        actor_user_id: UUID | None = None,
    ) -> int:
        raise NotImplementedError
