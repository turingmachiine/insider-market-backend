from fastapi import APIRouter

from src.notification_service.presentation.api.v1.routes.notifications import (
    router as notifications_router,
)

router = APIRouter(prefix="/v1")
router.include_router(notifications_router)

__all__ = ["router"]
