from uuid import UUID

from fastapi import HTTPException, status

from src.event_service.presentation.api.v1.schemas import EventResponse


def to_event_response(dto: object) -> EventResponse:
    return EventResponse(**dto.__dict__)


def event_not_found(event_id: UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Event {str(event_id)} not found",
    )


def bad_event_transition(exc: ValueError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(exc),
    )
