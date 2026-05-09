from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from src.rating_service.application.dto import (
    CreateAchievementDefinitionDTO,
    CreateRatingEventDTO,
)
from src.rating_service.application.usecases import RatingUseCases
from src.rating_service.presentation.api.v1.schemas import (
    AchievementDefinitionCreate,
    AchievementDefinitionListResponse,
    AchievementDefinitionResponse,
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
) -> RatingProfileListResponse:
    profiles = await rating_use_cases.get_leaderboard(limit=limit, offset=offset)
    return RatingProfileListResponse(
        items=[RatingProfileResponse(**item.__dict__) for item in profiles],
        total=await rating_use_cases.count_profiles(),
        limit=limit,
        offset=offset,
    )


@router.get("/profiles/{user_id}")
@inject
async def get_profile(
    user_id: UUID,
    rating_use_cases: FromDishka[RatingUseCases],
) -> RatingProfileResponse:
    profile = await rating_use_cases.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating profile for user {str(user_id)} not found",
        )
    return RatingProfileResponse(**profile.__dict__)


@router.post("/events", status_code=status.HTTP_201_CREATED)
@inject
async def record_event(
    event_data: RatingEventCreate,
    rating_use_cases: FromDishka[RatingUseCases],
) -> RatingEventResponse:
    dto = CreateRatingEventDTO(**event_data.model_dump())
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
) -> RatingProfileResponse:
    profile = await rating_use_cases.recalculate_user(user_id)
    return RatingProfileResponse(**profile.__dict__)


@router.post("/jobs/process-events")
@inject
async def process_pending_events(
    rating_use_cases: FromDishka[RatingUseCases],
    limit: LimitQuery = 100,
) -> RatingRecalculationResponse:
    result = await rating_use_cases.process_pending_events(limit=limit)
    return RatingRecalculationResponse(**result.__dict__)


@router.post("/jobs/dispatch-rewards")
@inject
async def dispatch_pending_rewards(
    rating_use_cases: FromDishka[RatingUseCases],
    limit: LimitQuery = 100,
) -> RatingRecalculationResponse:
    result = await rating_use_cases.dispatch_pending_rewards(limit=limit)
    return RatingRecalculationResponse(**result.__dict__)


@router.get("/achievements")
@inject
async def get_achievement_definitions(
    rating_use_cases: FromDishka[RatingUseCases],
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
) -> UserAchievementListResponse:
    achievements = await rating_use_cases.get_user_achievements(user_id)
    return UserAchievementListResponse(
        items=[UserAchievementResponse(**item.__dict__) for item in achievements]
    )


@router.get("/rewards/pending")
@inject
async def get_pending_rewards(
    rating_use_cases: FromDishka[RatingUseCases],
    limit: LimitQuery = 100,
) -> RewardTransactionListResponse:
    rewards = await rating_use_cases.get_pending_rewards(limit=limit)
    return RewardTransactionListResponse(
        items=[RewardTransactionResponse(**item.__dict__) for item in rewards]
    )
