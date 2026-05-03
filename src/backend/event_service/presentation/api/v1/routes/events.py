from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from src.backend.event_service.application.dto import (
    CancelEventDTO,
    CreateEventDTO,
    RejectEventDTO,
    ResolveEventDTO,
    UpdateEventDTO,
)
from src.backend.event_service.application.usecases import EventUseCases
from src.backend.event_service.domain.entities import EventStatus
from src.backend.event_service.presentation.api.v1.schemas import (
    EventCancel,
    EventCreate,
    EventListResponse,
    EventReject,
    EventResolve,
    EventResponse,
    EventUpdate,
)

router = APIRouter(prefix="/events", tags=["Events"])


def _to_response(dto: object) -> EventResponse:
    return EventResponse(**dto.__dict__)


def _not_found(event_id: UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Event {str(event_id)} not found",
    )


def _bad_transition(exc: ValueError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(exc),
    )


@router.get("")
@inject
async def get_events(
    event_use_cases: FromDishka[EventUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    status_filter: Annotated[EventStatus | None, Query(alias="status")] = None,
    source_rumor_id: UUID | None = None,
) -> EventListResponse:
    dtos = await event_use_cases.get_events(
        limit=limit,
        offset=offset,
        status=status_filter,
        source_rumor_id=source_rumor_id,
    )
    return EventListResponse(
        items=[_to_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/moderation-queue")
@inject
async def get_moderation_queue(
    event_use_cases: FromDishka[EventUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EventListResponse:
    dtos = await event_use_cases.get_moderation_queue(limit=limit, offset=offset)
    return EventListResponse(
        items=[_to_response(dto) for dto in dtos],
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
        raise _not_found(event_id)
    return _to_response(dto)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_event(
    event_data: EventCreate,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    dto = CreateEventDTO(**event_data.model_dump())
    result = await event_use_cases.create_event(dto)
    return _to_response(result)


@router.patch("/{event_id}")
@inject
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    dto = UpdateEventDTO(**event_data.model_dump())
    try:
        result = await event_use_cases.update_event(event_id, dto)
    except ValueError as exc:
        raise _bad_transition(exc) from exc
    if result is None:
        raise _not_found(event_id)
    return _to_response(result)


@router.post("/{event_id}/submit-moderation")
@inject
async def submit_event_for_moderation(
    event_id: UUID,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    try:
        result = await event_use_cases.submit_for_moderation(event_id)
    except ValueError as exc:
        raise _bad_transition(exc) from exc
    if result is None:
        raise _not_found(event_id)
    return _to_response(result)


@router.post("/{event_id}/approve")
@inject
async def approve_event(
    event_id: UUID,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    try:
        result = await event_use_cases.approve_event(event_id)
    except ValueError as exc:
        raise _bad_transition(exc) from exc
    if result is None:
        raise _not_found(event_id)
    return _to_response(result)


@router.post("/{event_id}/reject")
@inject
async def reject_event(
    event_id: UUID,
    event_data: EventReject,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    dto = RejectEventDTO(**event_data.model_dump())
    try:
        result = await event_use_cases.reject_event(event_id, dto)
    except ValueError as exc:
        raise _bad_transition(exc) from exc
    if result is None:
        raise _not_found(event_id)
    return _to_response(result)


@router.post("/{event_id}/resolve")
@inject
async def resolve_event(
    event_id: UUID,
    event_data: EventResolve,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    dto = ResolveEventDTO(**event_data.model_dump())
    try:
        result = await event_use_cases.resolve_event(event_id, dto)
    except ValueError as exc:
        raise _bad_transition(exc) from exc
    if result is None:
        raise _not_found(event_id)
    return _to_response(result)


@router.post("/{event_id}/cancel")
@inject
async def cancel_event(
    event_id: UUID,
    event_data: EventCancel,
    event_use_cases: FromDishka[EventUseCases],
) -> EventResponse:
    dto = CancelEventDTO(**event_data.model_dump())
    try:
        result = await event_use_cases.cancel_event(event_id, dto)
    except ValueError as exc:
        raise _bad_transition(exc) from exc
    if result is None:
        raise _not_found(event_id)
    return _to_response(result)
