"""Главный роутер API v1"""

from fastapi import APIRouter

from src.nsi_service.presentation.api.v1.routes import clubs, leagues, players, teams

router = APIRouter(prefix="/v1")

# Подключение роутеров
router.include_router(players.router)
router.include_router(clubs.router)
router.include_router(leagues.router)
router.include_router(teams.router)
