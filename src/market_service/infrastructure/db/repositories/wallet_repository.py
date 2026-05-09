from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.market_service.domain.entities import Wallet
from src.market_service.domain.interfaces.repositories import IWalletRepository
from src.market_service.infrastructure.db.tables import wallets_table


class WalletRepository(IWalletRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Wallet

    async def get_by_user_id(self, user_id: UUID) -> Wallet | None:
        query = select(self.model).where(wallets_table.c.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def save(self, wallet: Wallet) -> Wallet:
        self.session.add(wallet)
        await self.session.flush()
        return wallet
