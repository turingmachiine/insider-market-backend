from sqlalchemy.ext.asyncio import AsyncSession

from src.common.infrastructure.db import SQLAlchemyTransactionManager


class EventTransactionManager(SQLAlchemyTransactionManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
