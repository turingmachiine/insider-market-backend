from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.common.presentation.utils import can_access_user_resource, raise_forbidden
from src.rating_service.application.constants import RATING_ACCESS_DENIED_DETAIL
from src.rating_service.application.dto import (
    CreateAchievementDefinitionDTO,
    CreateRatingEventDTO,
)
from src.rating_service.application.usecases import RatingUseCases
from src.rating_service.presentation.api.v1.schemas import (
    AchievementDefinitionCreate,
    AchievementDefinitionListResponse,
    AchievementDefinitionResponse,
    LeaderboardEntryResponse,
    LeaderboardPeriod,
    LeaderboardResponse,
    RatingEventCreate,
    RatingEventResponse,
    RatingProfileListResponse,
    RatingProfileResponse,
    RatingRecalculationResponse,
    RewardTransactionListResponse,
    RewardTransactionResponse,
    UserAchievementListResponse,
    UserAchievementResponse,
)

router = APIRouter(prefix="/ratings", tags=["Ratings"])

LimitQuery = Annotated[int, Query(ge=1, le=500)]
OffsetQuery = Annotated[int, Query(ge=0)]


@router.get("/profiles")
@inject
async def get_profiles(
    rating_use_cases: FromDishka[RatingUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RATING_READ_ANY))],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> RatingProfileListResponse:
    profiles = await rating_use_cases.get_profiles(limit=limit, offset=offset)
    return RatingProfileListResponse(
        items=[RatingProfileResponse(**item.__dict__) for item in profiles],
        total=await rating_use_cases.count_profiles(),
        limit=limit,
        offset=offset,
    )


@router.get("/leaderboard")
@inject
async def get_leaderboard(
    rating_use_cases: FromDishka[RatingUseCases],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
    period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
) -> LeaderboardResponse:
    profiles = await rating_use_cases.get_leaderboard(limit=limit, offset=offset)
    items: list[LeaderboardEntryResponse] = []
    for index, profile in enumerate(profiles, start=offset + 1):
        achievements = await rating_use_cases.get_user_achievements(profile.user_id)
        items.append(
            LeaderboardEntryResponse(
                rank=index,
                profile=RatingProfileResponse(**profile.__dict__),
                achievements=[
                    UserAchievementResponse(**item.__dict__) for item in achievements
                ],
            )
        )
    return LeaderboardResponse(
        items=items,
        total=await rating_use_cases.count_profiles(),
        limit=limit,
        offset=offset,
        period=period,
    )


@router.get("/profiles/{user_id}")
@inject
async def get_profile(
    user_id: UUID,
    rating_use_cases: FromDishka[RatingUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.RATING_READ))
    ],
) -> RatingProfileResponse:
    profile = await rating_use_cases.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating profile for user {str(user_id)} not found",
        )
    if not can_access_user_resource(auth_payload, user_id, Permission.RATING_READ_ANY):
        raise_forbidden(RATING_ACCESS_DENIED_DETAIL)
    return RatingProfileResponse(**profile.__dict__)


@router.post("/events", status_code=status.HTTP_201_CREATED)
@inject
async def record_event(
    event_data: RatingEventCreate,
    rating_use_cases: FromDishka[RatingUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.RATING_WRITE))
    ],
) -> RatingEventResponse:
    event_payload = event_data.model_dump()
    event_payload["user_id"] = auth_payload.user_id
    dto = CreateRatingEventDTO(**event_payload)
    try:
        event = await rating_use_cases.record_event(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return RatingEventResponse(**event.__dict__)


@router.post("/profiles/{user_id}/recalculate")
@inject
async def recalculate_user(
    user_id: UUID,
    rating_use_cases: FromDishka[RatingUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.RATING_WRITE))
    ],
) -> RatingProfileResponse:
    if not can_access_user_resource(auth_payload, user_id, Permission.RATING_READ_ANY):
        raise_forbidden(RATING_ACCESS_DENIED_DETAIL)
    profile = await rating_use_cases.recalculate_user(user_id)
    return RatingProfileResponse(**profile.__dict__)


@router.post("/jobs/process-events")
@inject
async def process_pending_events(
    rating_use_cases: FromDishka[RatingUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RATING_JOBS_RUN))],
    limit: LimitQuery = 100,
) -> RatingRecalculationResponse:
    result = await rating_use_cases.process_pending_events(limit=limit)
    return RatingRecalculationResponse(**result.__dict__)


@router.post("/jobs/dispatch-rewards")
@inject
async def dispatch_pending_rewards(
    rating_use_cases: FromDishka[RatingUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RATING_JOBS_RUN))],
    limit: LimitQuery = 100,
) -> RatingRecalculationResponse:
    result = await rating_use_cases.dispatch_pending_rewards(limit=limit)
    return RatingRecalculationResponse(**result.__dict__)


@router.get("/achievements")
@inject
async def get_achievement_definitions(
    rating_use_cases: FromDishka[RatingUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RATING_READ))],
) -> AchievementDefinitionListResponse:
    definitions = await rating_use_cases.get_achievement_definitions()
    return AchievementDefinitionListResponse(
        items=[AchievementDefinitionResponse(**item.__dict__) for item in definitions]
    )


@router.post("/achievements", status_code=status.HTTP_201_CREATED)
@inject
async def create_achievement_definition(
    achievement_data: AchievementDefinitionCreate,
    rating_use_cases: FromDishka[RatingUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RATING_WRITE))],
) -> AchievementDefinitionResponse:
    dto = CreateAchievementDefinitionDTO(**achievement_data.model_dump())
    try:
        achievement = await rating_use_cases.create_achievement_definition(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return AchievementDefinitionResponse(**achievement.__dict__)


@router.get("/profiles/{user_id}/achievements")
@inject
async def get_user_achievements(
    user_id: UUID,
    rating_use_cases: FromDishka[RatingUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.RATING_READ))
    ],
) -> UserAchievementListResponse:
    if not can_access_user_resource(auth_payload, user_id, Permission.RATING_READ_ANY):
        raise_forbidden(RATING_ACCESS_DENIED_DETAIL)
    achievements = await rating_use_cases.get_user_achievements(user_id)
    return UserAchievementListResponse(
        items=[UserAchievementResponse(**item.__dict__) for item in achievements]
    )


@router.get("/rewards/pending")
@inject
async def get_pending_rewards(
    rating_use_cases: FromDishka[RatingUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RATING_READ_ANY))],
    limit: LimitQuery = 100,
) -> RewardTransactionListResponse:
    rewards = await rating_use_cases.get_pending_rewards(limit=limit)
    return RewardTransactionListResponse(
        items=[RewardTransactionResponse(**item.__dict__) for item in rewards]
    )
