from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.market_service.domain.entities import AuditLog, MarketAuditAction
from src.market_service.domain.interfaces.repositories import IAuditLogRepository
from src.market_service.infrastructure.db.tables import audit_logs_table


class AuditLogRepository(IAuditLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = AuditLog

    async def save(self, audit_log: AuditLog) -> AuditLog:
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        action: MarketAuditAction | None = None,
        actor_user_id: UUID | None = None,
    ) -> list[AuditLog]:
        query = select(self.model).order_by(audit_logs_table.c.created_at.desc())
        if action is not None:
            query = query.where(audit_logs_table.c.action == action)
        if actor_user_id is not None:
            query = query.where(audit_logs_table.c.actor_user_id == actor_user_id)
        result = await self.session.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def count_all(
        self,
        action: MarketAuditAction | None = None,
        actor_user_id: UUID | None = None,
    ) -> int:
        query = select(func.count()).select_from(audit_logs_table)
        if action is not None:
            query = query.where(audit_logs_table.c.action == action)
        if actor_user_id is not None:
            query = query.where(audit_logs_table.c.actor_user_id == actor_user_id)
        result = await self.session.execute(query)
        return int(result.scalar_one())
