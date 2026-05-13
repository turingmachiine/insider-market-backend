from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.common.application.request_context import RequestContextProvider
from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.common.presentation.utils import can_access_user_resource, raise_forbidden
from src.market_service.application.constants import WALLET_ACCESS_DENIED_DETAIL
from src.market_service.application.dto import CreateWalletDTO
from src.market_service.application.usecases import WalletUseCases
from src.market_service.presentation.api.v1.schemas import WalletCreate, WalletResponse

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get("/{user_id}")
@inject
async def get_wallet(
    user_id: UUID,
    wallet_use_cases: FromDishka[WalletUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.MARKET_READ))
    ],
) -> WalletResponse:
    dto = await wallet_use_cases.get_wallet(user_id)
    if dto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet for user {str(user_id)} not found",
        )
    if not can_access_user_resource(auth_payload, user_id, Permission.WALLET_READ_ANY):
        raise_forbidden(WALLET_ACCESS_DENIED_DETAIL)
    return WalletResponse(**dto.__dict__)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_wallet(
    wallet_data: WalletCreate,
    request_context_provider: FromDishka[RequestContextProvider],
    wallet_use_cases: FromDishka[WalletUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.MARKET_WRITE))
    ],
) -> WalletResponse:
    wallet_payload = wallet_data.model_dump()
    wallet_payload["user_id"] = auth_payload.user_id
    dto = CreateWalletDTO(**wallet_payload)
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
