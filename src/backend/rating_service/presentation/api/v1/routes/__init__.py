from fastapi import APIRouter

from src.backend.rating_service.presentation.api.v1.routes.ratings import (
    router as ratings_router,
)

router = APIRouter(prefix="/v1")
router.include_router(ratings_router)

__all__ = ["router"]
