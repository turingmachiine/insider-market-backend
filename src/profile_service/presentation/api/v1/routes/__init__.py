from fastapi import APIRouter

from src.profile_service.presentation.api.v1.routes import profiles

router = APIRouter(prefix="/v1")

router.include_router(profiles.router)
router.include_router(profiles.achievements_router)
