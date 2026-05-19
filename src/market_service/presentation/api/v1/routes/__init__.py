from fastapi import APIRouter

from src.market_service.presentation.api.v1.routes import (
    internal_wallets,
    markets,
    wallets,
)

router = APIRouter(prefix="/v1")

router.include_router(internal_wallets.router)
router.include_router(markets.router)
router.include_router(wallets.router)
