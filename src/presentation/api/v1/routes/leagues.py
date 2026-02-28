"""API endpoints для лиг"""

import logging
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from src.application.dto import CreateLeagueDTO
from src.application.usecases import LeagueUseCases
from src.presentation.api.v1.mappers import ILeagueResponseMapper
from src.presentation.api.v1.schemas import (
    LeagueCreate,
    LeagueListResponse,
    LeagueResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leagues", tags=["Leagues"])


@router.get("", response_model=LeagueListResponse)
@inject
async def get_all_leagues(
    league_use_cases: FromDishka[LeagueUseCases],
    response_mapper: FromDishka[ILeagueResponseMapper],
    limit: int = Query(  # noqa: B008
        50, ge=1, le=200, description="Максимальное количество результатов"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),  # noqa: B008
) -> LeagueListResponse:
    """Получить все лиги с пагинацией"""
    dtos = await league_use_cases.get_all_leagues(limit=limit, offset=offset)
    return LeagueListResponse(
        items=[response_mapper.to_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/top", response_model=list[LeagueResponse])
@inject
async def get_top_leagues(
    league_use_cases: FromDishka[LeagueUseCases],
    response_mapper: FromDishka[ILeagueResponseMapper],
    limit: int = Query(  # noqa: B008
        10, ge=1, le=50, description="Максимальное количество результатов"
    ),
) -> list[LeagueResponse]:
    """Получить топ лиги"""
    dtos = await league_use_cases.get_top_leagues(limit=limit)
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/search", response_model=list[LeagueResponse])
@inject
async def search_leagues(
    league_use_cases: FromDishka[LeagueUseCases],
    response_mapper: FromDishka[ILeagueResponseMapper],
    name: str = Query(  # noqa: B008
        ..., min_length=2, description="Название лиги для поиска"
    ),
) -> list[LeagueResponse]:
    """Поиск лиг по названию"""
    dtos = await league_use_cases.search_leagues(name=name)
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/{league_id}", response_model=LeagueResponse)
@inject
async def get_league(
    league_id: UUID,
    league_use_cases: FromDishka[LeagueUseCases],
    response_mapper: FromDishka[ILeagueResponseMapper],
) -> LeagueResponse:
    """Получить лигу по ID"""
    dto = await league_use_cases.get_league(league_id)
    if not dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League {league_id} not found",
        )
    return response_mapper.to_response(dto)


@router.post("", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_league(
    league_data: LeagueCreate,
    league_use_cases: FromDishka[LeagueUseCases],
    response_mapper: FromDishka[ILeagueResponseMapper],
) -> LeagueResponse:
    """Создать новую лигу"""
    dto = CreateLeagueDTO(**league_data.model_dump())
    result_dto = await league_use_cases.create_league(dto)
    return response_mapper.to_response(result_dto)
