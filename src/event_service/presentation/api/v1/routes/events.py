from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.common.presentation.utils import raise_forbidden
from src.event_service.application.constants import EVENT_ACCESS_DENIED_DETAIL
from src.event_service.application.dto import (
    CancelEventDTO,
    CreateEventDTO,
    RejectEventDTO,
    ResolveEventDTO,
    UpdateEventDTO,
)
from src.event_service.application.usecases import EventUseCases
from src.event_service.domain.entities import EventCategory, EventSort, EventStatus
from src.event_service.presentation.api.v1.schemas import (
    EventCancel,
    EventCreate,
    EventListResponse,
    EventProposalCreate,
    EventReject,
    EventResolve,
    EventResponse,
    EventUpdate,
)
from src.event_service.presentation.api.v1.utils import (
    bad_event_transition,
    event_not_found,
    to_event_response,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("")
@inject
async def get_events(
    event_use_cases: FromDishka[EventUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    status_filter: Annotated[EventStatus | None, Query(alias="status")] = None,
    category: EventCategory | None = None,
    sort: EventSort = EventSort.CREATED_AT,
    source_rumor_id: UUID | None = None,
) -> EventListResponse:
    dtos = await event_use_cases.get_events(
        limit=limit,
        offset=offset,
        status=status_filter,
        source_rumor_id=source_rumor_id,
        category=category,
        sort=sort,
    )
    return EventListResponse(
        items=[to_event_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/moderation-queue")
@inject
async def get_moderation_queue(
    event_use_cases: FromDishka[EventUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.EVENT_READ))],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EventListResponse:
    dtos = await event_use_cases.get_moderation_queue(limit=limit, offset=offset)
    return EventListResponse(
        items=[to_event_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}")
@inject
async def get_event(
    event_id: UUID,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    dto = await event_use_cases.get_event(event_id)
    if dto is None:
        raise event_not_found(event_id)
    return to_event_response(dto)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_event(
    event_data: EventCreate,
    event_use_cases: FromDishka[EventUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.EVENT_WRITE))
    ],
) -> EventResponse:
    event_payload = event_data.model_dump()
    event_payload["created_by_user_id"] = auth_payload.user_id
    dto = CreateEventDTO(**event_payload)
    result = await event_use_cases.create_event(dto)
    return to_event_response(result)


@router.post("/proposals", status_code=status.HTTP_201_CREATED)
@inject
async def propose_event(
    event_data: EventProposalCreate,
    event_use_cases: FromDishka[EventUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.EVENT_WRITE))
    ],
) -> EventResponse:
    event_payload = event_data.model_dump()
    event_payload["created_by_user_id"] = auth_payload.user_id
    dto = CreateEventDTO(**event_payload)
    result = await event_use_cases.create_event(dto)
    return to_event_response(result)


@router.patch("/{event_id}")
@inject
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    event_use_cases: FromDishka[EventUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.EVENT_WRITE))
    ],
) -> EventResponse:
    dto = UpdateEventDTO(**event_data.model_dump())
    try:
        result = await event_use_cases.update_event(
            event_id,
            dto,
            owner_user_id=auth_payload.user_id,
        )
    except PermissionError:
        raise_forbidden(EVENT_ACCESS_DENIED_DETAIL)
    except ValueError as exc:
        raise bad_event_transition(exc) from exc
    if result is None:
        raise event_not_found(event_id)
    return to_event_response(result)


@router.post("/{event_id}/submit-moderation")
@inject
async def submit_event_for_moderation(
    event_id: UUID,
    event_use_cases: FromDishka[EventUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.EVENT_WRITE))
    ],
) -> EventResponse:
    try:
        result = await event_use_cases.submit_for_moderation(
            event_id,
            owner_user_id=auth_payload.user_id,
        )
    except PermissionError:
        raise_forbidden(EVENT_ACCESS_DENIED_DETAIL)
    except ValueError as exc:
        raise bad_event_transition(exc) from exc
    if result is None:
        raise event_not_found(event_id)
    return to_event_response(result)


@router.post("/{event_id}/approve")
@inject
async def approve_event(
    event_id: UUID,
    event_use_cases: FromDishka[EventUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.EVENT_MODERATE))],
) -> EventResponse:
    try:
        result = await event_use_cases.approve_event(event_id)
    except ValueError as exc:
        raise bad_event_transition(exc) from exc
    if result is None:
        raise event_not_found(event_id)
    return to_event_response(result)


@router.post("/{event_id}/reject")
@inject
async def reject_event(
    event_id: UUID,
    event_data: EventReject,
    event_use_cases: FromDishka[EventUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.EVENT_MODERATE))],
) -> EventResponse:
    dto = RejectEventDTO(**event_data.model_dump())
    try:
        result = await event_use_cases.reject_event(event_id, dto)
    except ValueError as exc:
        raise bad_event_transition(exc) from exc
    if result is None:
        raise event_not_found(event_id)
    return to_event_response(result)


@router.post("/{event_id}/resolve")
@inject
async def resolve_event(
    event_id: UUID,
    event_data: EventResolve,
    event_use_cases: FromDishka[EventUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.EVENT_MODERATE))
    ],
) -> EventResponse:
    event_payload = event_data.model_dump()
    event_payload["resolved_by_user_id"] = auth_payload.user_id
    dto = ResolveEventDTO(**event_payload)
    try:
        result = await event_use_cases.resolve_event(event_id, dto)
    except ValueError as exc:
        raise bad_event_transition(exc) from exc
    if result is None:
        raise event_not_found(event_id)
    return to_event_response(result)


@router.post("/{event_id}/cancel")
@inject
async def cancel_event(
    event_id: UUID,
    event_data: EventCancel,
    event_use_cases: FromDishka[EventUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.EVENT_MODERATE))],
) -> EventResponse:
    dto = CancelEventDTO(**event_data.model_dump())
    try:
        result = await event_use_cases.cancel_event(event_id, dto)
    except ValueError as exc:
        raise bad_event_transition(exc) from exc
    if result is None:
        raise event_not_found(event_id)
    return to_event_response(result)
