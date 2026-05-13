from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.admin_service.application.dto import (
    EventModerationCommandDTO,
    SavedFilterCreateDTO,
    UserRoleGrantDTO,
    UserStatusUpdateDTO,
)
from src.admin_service.application.usecases import AdminUseCases
from src.admin_service.presentation.api.v1.schemas import (
    AdminActionListResponse,
    AdminActionResponse,
    AdminDashboardResponse,
    EventModerationCommandRequest,
    EventModerationQueueResponse,
    HealthStatusResponse,
    ProfileSummaryResponse,
    SavedFilterCreateRequest,
    SavedFilterListResponse,
    SavedFilterResponse,
    UserListResponse,
    UserRoleGrantRequest,
    UserStatusUpdateRequest,
    UserSummaryResponse,
)
from src.common.application.request_context import RequestContextProvider
from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission

router = APIRouter(prefix="/v1", tags=["Admin"])

LimitQuery = Annotated[int, Query(ge=1, le=500)]
OffsetQuery = Annotated[int, Query(ge=0)]


@router.get("/dashboard")
@inject
async def get_dashboard(
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
) -> AdminDashboardResponse:
    result = await admin_use_cases.get_dashboard_overview()
    return AdminDashboardResponse(
        services=[
            HealthStatusResponse(**service.__dict__) for service in result.services
        ],
        event_moderation_queue_size=result.event_moderation_queue_size,
        users_total=result.users_total,
        rating_leaderboard_size=result.rating_leaderboard_size,
        profiles_total=result.profiles_total,
    )


@router.get("/health")
@inject
async def get_system_health(
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
) -> list[HealthStatusResponse]:
    services = await admin_use_cases.get_system_health()
    return [HealthStatusResponse(**service.__dict__) for service in services]


@router.get("/events/moderation-queue")
@inject
async def get_event_moderation_queue(
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> EventModerationQueueResponse:
    queue = await admin_use_cases.get_event_moderation_queue(limit=limit, offset=offset)
    return EventModerationQueueResponse(**queue.__dict__)


@router.post("/events/{event_id}/submit-moderation")
@inject
async def submit_event_for_moderation(
    event_id: UUID,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> dict:
    return await admin_use_cases.submit_event_for_moderation(
        event_id,
        actor_user_id=payload.user_id,
        correlation_id=request_context_provider.get_context().correlation_id,
    )


@router.post("/events/{event_id}/approve")
@inject
async def approve_event(
    event_id: UUID,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> dict:
    return await admin_use_cases.approve_event(
        event_id,
        actor_user_id=payload.user_id,
        correlation_id=request_context_provider.get_context().correlation_id,
    )


@router.post("/events/{event_id}/reject")
@inject
async def reject_event(
    event_id: UUID,
    request: EventModerationCommandRequest,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> dict:
    return await admin_use_cases.reject_event(
        event_id,
        notes=request.notes,
        actor_user_id=payload.user_id,
        correlation_id=request_context_provider.get_context().correlation_id,
    )


@router.post("/events/{event_id}/resolve")
@inject
async def resolve_event(
    event_id: UUID,
    request: EventModerationCommandRequest,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> dict:
    dto = EventModerationCommandDTO(**request.model_dump())
    return await admin_use_cases.resolve_event(
        event_id,
        dto,
        actor_user_id=payload.user_id,
        correlation_id=request_context_provider.get_context().correlation_id,
    )


@router.post("/events/{event_id}/cancel")
@inject
async def cancel_event(
    event_id: UUID,
    request: EventModerationCommandRequest,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> dict:
    return await admin_use_cases.cancel_event(
        event_id,
        notes=request.notes,
        actor_user_id=payload.user_id,
        correlation_id=request_context_provider.get_context().correlation_id,
    )


@router.get("/users")
@inject
async def get_users(
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> UserListResponse:
    users = await admin_use_cases.get_users(limit=limit, offset=offset)
    return UserListResponse(
        items=[UserSummaryResponse(**item.__dict__) for item in users.items],
        total=users.total,
        limit=users.limit,
        offset=users.offset,
    )


@router.get("/users/{user_id}")
@inject
async def get_user(
    user_id: UUID,
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
) -> UserSummaryResponse:
    user = await admin_use_cases.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {str(user_id)} not found",
        )
    return UserSummaryResponse(**user.__dict__)


@router.get("/users/{user_id}/permissions")
@inject
async def get_user_permissions(
    user_id: UUID,
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
) -> dict[str, object]:
    return await admin_use_cases.get_user_permissions(user_id)


@router.patch("/users/{user_id}/status")
@inject
async def set_user_status(
    user_id: UUID,
    request: UserStatusUpdateRequest,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> UserSummaryResponse:
    user = await admin_use_cases.set_user_status(
        user_id,
        UserStatusUpdateDTO(is_active=request.is_active),
        actor_user_id=payload.user_id,
        correlation_id=request_context_provider.get_context().correlation_id,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {str(user_id)} not found",
        )
    return UserSummaryResponse(**user.__dict__)


@router.post("/users/{user_id}/roles")
@inject
async def assign_role(
    user_id: UUID,
    request: UserRoleGrantRequest,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> UserSummaryResponse:
    user = await admin_use_cases.assign_role(
        user_id,
        UserRoleGrantDTO(role_name=request.role_name),
        actor_user_id=payload.user_id,
        correlation_id=request_context_provider.get_context().correlation_id,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {str(user_id)} not found",
        )
    return UserSummaryResponse(**user.__dict__)


@router.get("/profiles/{user_id}/summary")
@inject
async def get_profile_summary(
    user_id: UUID,
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
) -> ProfileSummaryResponse:
    summary = await admin_use_cases.get_profile_summary(user_id)
    return ProfileSummaryResponse(**summary.__dict__)


@router.get("/audit/actions")
@inject
async def get_audit_actions(
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> AdminActionListResponse:
    actions = await admin_use_cases.get_audit_actions(limit=limit, offset=offset)
    return AdminActionListResponse(
        items=[AdminActionResponse(**item.__dict__) for item in actions.items],
        total=actions.total,
        limit=actions.limit,
        offset=actions.offset,
    )


@router.get("/saved-filters")
@inject
async def get_saved_filters(
    admin_use_cases: FromDishka[AdminUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.ADMIN_READ))],
    limit: LimitQuery = 100,
    offset: OffsetQuery = 0,
) -> SavedFilterListResponse:
    filters = await admin_use_cases.get_saved_filters(limit=limit, offset=offset)
    return SavedFilterListResponse(
        items=[SavedFilterResponse(**item.__dict__) for item in filters.items],
        total=filters.total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post("/saved-filters", status_code=status.HTTP_201_CREATED)
@inject
async def save_filter(
    request: SavedFilterCreateRequest,
    request_context_provider: FromDishka[RequestContextProvider],
    admin_use_cases: FromDishka[AdminUseCases],
    payload: Annotated[
        UserContext,
        Depends(require_permission(Permission.ADMIN_WRITE)),
    ],
) -> SavedFilterResponse:
    dto = SavedFilterCreateDTO(
        actor_user_id=payload.user_id,
        name=request.name,
        scope=request.scope,
        criteria=request.criteria,
    )
    saved_filter = await admin_use_cases.save_filter(
        dto,
        correlation_id=request_context_provider.get_context().correlation_id,
    )
    return SavedFilterResponse(**saved_filter.__dict__)
