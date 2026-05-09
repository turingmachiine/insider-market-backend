from fastapi import APIRouter

from src.rumor_service.presentation.api.v1.routes import (
    raw_publications,
    rumors,
    sources,
)

router = APIRouter(prefix="/v1")

router.include_router(sources.router)
router.include_router(raw_publications.router)
router.include_router(rumors.router)
