from uuid import UUID, uuid4

from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager
from src.market_service.application.dto import CreateWalletDTO, WalletDTO
from src.market_service.application.mappers import IWalletMapper
from src.market_service.core.money import quantize_coin
from src.market_service.domain.entities import AuditLog, MarketAuditAction, Wallet
from src.market_service.domain.interfaces.repositories import (
    IAuditLogRepository,
    IWalletRepository,
)


@use_case
class WalletUseCases(HasTransactionManager):
    wallet_repository: IWalletRepository
    audit_log_repository: IAuditLogRepository
    wallet_mapper: IWalletMapper
    transaction_manager: TransactionManager

    async def get_wallet(self, user_id: UUID) -> WalletDTO | None:
        wallet = await self.wallet_repository.get_by_user_id(user_id)
        return self.wallet_mapper.to_dto(wallet) if wallet else None

    @transactional()
    async def create_wallet(
        self,
        dto: CreateWalletDTO,
        correlation_id: str | None = None,
    ) -> WalletDTO:
        existing_wallet = await self.wallet_repository.get_by_user_id(dto.user_id)
        if existing_wallet is not None:
            raise ValueError(f"Wallet for user {str(dto.user_id)} already exists")
        if dto.initial_balance < 0:
            raise ValueError("Initial balance must not be negative")
        wallet = Wallet(
            id=uuid4(),
            user_id=dto.user_id,
            balance=quantize_coin(dto.initial_balance),
        )
        saved_wallet = await self.wallet_repository.save(wallet)
        await self.audit_log_repository.save(
            AuditLog(
                id=uuid4(),
                actor_user_id=dto.user_id,
                action=MarketAuditAction.WALLET_CREATE,
                target_type="wallet",
                target_id=str(saved_wallet.id),
                after={
                    "user_id": str(saved_wallet.user_id),
                    "balance": str(saved_wallet.balance),
                },
                correlation_id=correlation_id,
            )
        )
        return self.wallet_mapper.to_dto(saved_wallet)


__all__ = ["WalletUseCases"]
