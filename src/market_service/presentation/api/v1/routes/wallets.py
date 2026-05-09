from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, status

from src.market_service.application.dto import CreateWalletDTO
from src.market_service.application.usecases import WalletUseCases
from src.market_service.presentation.api.v1.schemas import WalletCreate, WalletResponse

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get("/{user_id}")
@inject
async def get_wallet(
    user_id: UUID,
    wallet_use_cases: FromDishka[WalletUseCases],
) -> WalletResponse:
    dto = await wallet_use_cases.get_wallet(user_id)
    if dto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet for user {str(user_id)} not found",
        )
    return WalletResponse(**dto.__dict__)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_wallet(
    wallet_data: WalletCreate,
    wallet_use_cases: FromDishka[WalletUseCases],
) -> WalletResponse:
    dto = CreateWalletDTO(**wallet_data.model_dump())
    try:
        result = await wallet_use_cases.create_wallet(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return WalletResponse(**result.__dict__)
