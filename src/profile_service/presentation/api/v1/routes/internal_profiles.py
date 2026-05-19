from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.common.application.service_context import ServiceContext
from src.common.domain.service_auth import (
    PROFILE_BALANCE_WRITE_SCOPE,
    PROFILE_CREATE_SCOPE,
)
from src.common.presentation.decorators import require_service_auth
from src.profile_service.application.dto import BalanceOperationDTO, CreateProfileDTO
from src.profile_service.application.usecases import ProfileUseCases
from src.profile_service.presentation.api.v1.schemas import (
    BalanceOperation,
    BalanceTransactionResponse,
    ProfileCreate,
    ProfileResponse,
)

router = APIRouter(prefix="/internal/profiles", tags=["Internal Profiles"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_profile(
    profile_data: ProfileCreate,
    profile_use_cases: FromDishka[ProfileUseCases],
    _: Annotated[
        ServiceContext,
        Depends(require_service_auth(PROFILE_CREATE_SCOPE)),
    ],
) -> ProfileResponse:
    dto = CreateProfileDTO(**profile_data.model_dump())
    try:
        result = await profile_use_cases.create_profile(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return ProfileResponse(**result.__dict__)


@router.post(
    "/{user_id}/balance/transactions",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def apply_balance_operation(
    user_id: UUID,
    operation_data: BalanceOperation,
    profile_use_cases: FromDishka[ProfileUseCases],
    _: Annotated[
        ServiceContext,
        Depends(require_service_auth(PROFILE_BALANCE_WRITE_SCOPE)),
    ],
) -> BalanceTransactionResponse:
    dto = BalanceOperationDTO(**operation_data.model_dump())
    try:
        transaction = await profile_use_cases.apply_balance_operation(user_id, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {str(user_id)} not found",
        )
    return BalanceTransactionResponse(**transaction.__dict__)
