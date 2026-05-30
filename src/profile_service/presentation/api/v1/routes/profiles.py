from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.common.presentation.utils import (
    can_access_user_resource,
    raise_forbidden,
    require_user_owner,
)
from src.profile_service.application.constants import PROFILE_ACCESS_DENIED_DETAIL
from src.profile_service.application.dto import (
    AwardAchievementDTO,
    BalanceOperationDTO,
    CreateAchievementDTO,
    CreateActivityDTO,
    CreateProfileDTO,
    UpdateProfileDTO,
)
from src.profile_service.application.usecases import ProfileUseCases
from src.profile_service.domain.entities import ActivityType
from src.profile_service.presentation.api.v1.schemas import (
    AchievementCreate,
    AchievementResponse,
    ActivityCreate,
    ActivityListResponse,
    ActivityResponse,
    AwardAchievement,
    BalanceOperation,
    BalanceResponse,
    BalanceTransactionListResponse,
    BalanceTransactionResponse,
    ProfileCreate,
    ProfileListResponse,
    ProfileResponse,
    ProfileUpdate,
    PublicProfileResponse,
    UserAchievementListResponse,
    UserAchievementResponse,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])
achievements_router = APIRouter(prefix="/achievements", tags=["Achievements"])

LimitQuery = Annotated[int, Query(ge=1, le=500)]
OffsetQuery = Annotated[int, Query(ge=0)]
ActivityTypeQuery = Annotated[ActivityType | None, Query()]


@router.get("")
@inject
async def get_profiles(
    profile_use_cases: FromDishka[ProfileUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.PROFILE_READ_ANY))],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> ProfileListResponse:
    profiles = await profile_use_cases.get_profiles(limit=limit, offset=offset)
    total = await profile_use_cases.count_profiles()
    return ProfileListResponse(
        items=[ProfileResponse(**profile.__dict__) for profile in profiles],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_profile(
    profile_data: ProfileCreate,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_WRITE))
    ],
) -> ProfileResponse:
    profile_payload = profile_data.model_dump()
    profile_payload["user_id"] = auth_payload.user_id
    dto = CreateProfileDTO(**profile_payload)
    try:
        result = await profile_use_cases.create_profile(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return ProfileResponse(**result.__dict__)


@router.get("/public/{user_id}")
@inject
async def get_public_profile(
    user_id: UUID,
    profile_use_cases: FromDishka[ProfileUseCases],
) -> PublicProfileResponse:
    profile = await profile_use_cases.get_public_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Public profile for user {str(user_id)} not found",
        )
    return PublicProfileResponse(**profile.__dict__)


@router.get("/{user_id}")
@inject
async def get_profile(
    user_id: UUID,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_READ))
    ],
) -> ProfileResponse:
    profile = await profile_use_cases.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {str(user_id)} not found",
        )
    if not can_access_user_resource(auth_payload, user_id, Permission.PROFILE_READ_ANY):
        raise_forbidden(PROFILE_ACCESS_DENIED_DETAIL)
    return ProfileResponse(**profile.__dict__)


@router.patch("/{user_id}")
@inject
async def update_profile(
    user_id: UUID,
    profile_data: ProfileUpdate,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_WRITE))
    ],
) -> ProfileResponse:
    require_user_owner(auth_payload, user_id, PROFILE_ACCESS_DENIED_DETAIL)
    dto = UpdateProfileDTO(**profile_data.model_dump(exclude_unset=True))
    try:
        profile = await profile_use_cases.update_profile(user_id, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {str(user_id)} not found",
        )
    return ProfileResponse(**profile.__dict__)


@router.get("/{user_id}/balance")
@inject
async def get_balance(
    user_id: UUID,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_READ))
    ],
) -> BalanceResponse:
    balance = await profile_use_cases.get_balance(user_id)
    if balance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {str(user_id)} not found",
        )
    if not can_access_user_resource(auth_payload, user_id, Permission.PROFILE_READ_ANY):
        raise_forbidden(PROFILE_ACCESS_DENIED_DETAIL)
    return BalanceResponse(**balance.__dict__)


@router.post("/{user_id}/balance/transactions", status_code=status.HTTP_201_CREATED)
@inject
async def apply_balance_operation(
    user_id: UUID,
    operation_data: BalanceOperation,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_WRITE))
    ],
) -> BalanceTransactionResponse:
    require_user_owner(auth_payload, user_id, PROFILE_ACCESS_DENIED_DETAIL)
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


@router.get("/{user_id}/balance/transactions")
@inject
async def get_balance_transactions(
    user_id: UUID,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_READ))
    ],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> BalanceTransactionListResponse:
    if not can_access_user_resource(auth_payload, user_id, Permission.PROFILE_READ_ANY):
        raise_forbidden(PROFILE_ACCESS_DENIED_DETAIL)
    transactions = await profile_use_cases.get_balance_transactions(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return BalanceTransactionListResponse(
        items=[BalanceTransactionResponse(**item.__dict__) for item in transactions]
    )


@router.get("/{user_id}/activity")
@inject
async def get_activity(
    user_id: UUID,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_READ))
    ],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
    activity_type: ActivityTypeQuery = None,
) -> ActivityListResponse:
    if not can_access_user_resource(auth_payload, user_id, Permission.PROFILE_READ_ANY):
        raise_forbidden(PROFILE_ACCESS_DENIED_DETAIL)
    activities = await profile_use_cases.get_activity(
        user_id=user_id,
        limit=limit,
        offset=offset,
        activity_type=activity_type,
    )
    return ActivityListResponse(
        items=[ActivityResponse(**item.__dict__) for item in activities]
    )


@router.post("/{user_id}/activity", status_code=status.HTTP_201_CREATED)
@inject
async def add_activity(
    user_id: UUID,
    activity_data: ActivityCreate,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_WRITE))
    ],
) -> ActivityResponse:
    require_user_owner(auth_payload, user_id, PROFILE_ACCESS_DENIED_DETAIL)
    dto = CreateActivityDTO(**activity_data.model_dump())
    try:
        activity = await profile_use_cases.add_activity(user_id, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {str(user_id)} not found",
        )
    return ActivityResponse(**activity.__dict__)


@achievements_router.get("")
@inject
async def get_achievements(
    profile_use_cases: FromDishka[ProfileUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.PROFILE_READ))],
) -> list[AchievementResponse]:
    achievements = await profile_use_cases.get_achievements()
    return [AchievementResponse(**item.__dict__) for item in achievements]


@achievements_router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_achievement(
    achievement_data: AchievementCreate,
    profile_use_cases: FromDishka[ProfileUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.PROFILE_WRITE))],
) -> AchievementResponse:
    dto = CreateAchievementDTO(**achievement_data.model_dump())
    try:
        achievement = await profile_use_cases.create_achievement(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return AchievementResponse(**achievement.__dict__)


@router.get("/{user_id}/achievements")
@inject
async def get_user_achievements(
    user_id: UUID,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_READ))
    ],
) -> UserAchievementListResponse:
    if not can_access_user_resource(auth_payload, user_id, Permission.PROFILE_READ_ANY):
        raise_forbidden(PROFILE_ACCESS_DENIED_DETAIL)
    achievements = await profile_use_cases.get_user_achievements(user_id)
    return UserAchievementListResponse(
        items=[UserAchievementResponse(**item.__dict__) for item in achievements]
    )


@router.post("/{user_id}/achievements", status_code=status.HTTP_201_CREATED)
@inject
async def award_achievement(
    user_id: UUID,
    achievement_data: AwardAchievement,
    profile_use_cases: FromDishka[ProfileUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.PROFILE_WRITE))
    ],
) -> UserAchievementResponse:
    require_user_owner(auth_payload, user_id, PROFILE_ACCESS_DENIED_DETAIL)
    dto = AwardAchievementDTO(**achievement_data.model_dump())
    try:
        achievement = await profile_use_cases.award_achievement(user_id, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if achievement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {str(user_id)} not found",
        )
    return UserAchievementResponse(**achievement.__dict__)
