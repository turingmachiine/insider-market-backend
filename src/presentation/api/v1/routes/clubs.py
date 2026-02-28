"""API endpoints для клубов"""

import logging
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from src.application.dto import CreateClubDTO
from src.application.usecases import ClubUseCases
from src.presentation.api.v1.mappers import IClubResponseMapper
from src.presentation.api.v1.schemas import ClubCreate, ClubListResponse, ClubResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("", response_model=ClubListResponse)
@inject
async def get_all_clubs(
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
    limit: int = Query(  # noqa: B008
        100, ge=1, le=500, description="Максимальное количество результатов"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),  # noqa: B008
) -> ClubListResponse:
    """Получить все клубы с пагинацией"""
    dtos = await club_use_cases.get_all_clubs(limit=limit, offset=offset)
    return ClubListResponse(
        items=[response_mapper.to_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=list[ClubResponse])
@inject
async def search_clubs(
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
    name: str = Query(  # noqa: B008
        ..., min_length=2, description="Название клуба для поиска"
    ),
) -> list[ClubResponse]:
    """Поиск клубов по названию"""
    dtos = await club_use_cases.search_clubs(name=name)
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/{club_id}", response_model=ClubResponse)
@inject
async def get_club(
    club_id: UUID,
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
) -> ClubResponse:
    """Получить клуб по ID"""
    dto = await club_use_cases.get_club(club_id)
    if not dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Club {club_id} not found",
        )
    return response_mapper.to_response(dto)


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_club(
    club_data: ClubCreate,
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
) -> ClubResponse:
    """Создать новый клуб"""
    dto = CreateClubDTO(**club_data.model_dump())
    result_dto = await club_use_cases.create_club(dto)
    return response_mapper.to_response(result_dto)


@router.get("/league/{league_id}", response_model=list[ClubResponse])
@inject
async def get_clubs_by_league(
    league_id: UUID,
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
    limit: int = Query(50, ge=1, le=200),  # noqa: B008
) -> list[ClubResponse]:
    """Получить клубы лиги"""
    dtos = await club_use_cases.get_clubs_by_league(league_id=league_id, limit=limit)
    return [response_mapper.to_response(dto) for dto in dtos]
