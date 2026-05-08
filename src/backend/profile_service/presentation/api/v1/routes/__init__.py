from fastapi import APIRouter

from src.backend.profile_service.presentation.api.v1.routes import profiles

router = APIRouter(prefix="/v1")

router.include_router(profiles.router)
