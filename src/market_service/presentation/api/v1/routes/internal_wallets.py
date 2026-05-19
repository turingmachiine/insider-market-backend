from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.common.application.request_context import RequestContextProvider
from src.common.application.service_context import ServiceContext
from src.common.domain.service_auth import WALLET_CREATE_SCOPE
from src.common.presentation.decorators import require_service_auth
from src.market_service.application.dto import CreateWalletDTO
from src.market_service.application.usecases import WalletUseCases
from src.market_service.presentation.api.v1.schemas import WalletCreate, WalletResponse

router = APIRouter(prefix="/internal/wallets", tags=["Internal Wallets"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_wallet(
    wallet_data: WalletCreate,
    request_context_provider: FromDishka[RequestContextProvider],
    wallet_use_cases: FromDishka[WalletUseCases],
    _: Annotated[
        ServiceContext,
        Depends(require_service_auth(WALLET_CREATE_SCOPE)),
    ],
) -> WalletResponse:
    dto = CreateWalletDTO(**wallet_data.model_dump())
    try:
        result = await wallet_use_cases.create_wallet(
            dto,
            correlation_id=request_context_provider.get_context().correlation_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return WalletResponse(**result.__dict__)


__all__ = ["router"]
