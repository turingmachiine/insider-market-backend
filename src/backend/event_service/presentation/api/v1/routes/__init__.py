from fastapi import APIRouter

from src.backend.event_service.presentation.api.v1.routes.events import (
    router as events_router,
)

router = APIRouter(prefix="/v1")
router.include_router(events_router)

__all__ = ["events_router", "router"]
