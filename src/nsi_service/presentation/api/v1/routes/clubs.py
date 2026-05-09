"""API endpoints для клубов"""

import logging
from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.nsi_service.application.dto import CreateClubDTO
from src.nsi_service.application.usecases import ClubUseCases
from src.nsi_service.presentation.api.v1.mappers import IClubResponseMapper
from src.nsi_service.presentation.api.v1.schemas import (
    ClubCreate,
    ClubListResponse,
    ClubResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("")
@inject
async def get_all_clubs(
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
    limit: Annotated[
        int,
        Query(ge=1, le=500, description="Максимальное количество результатов"),
    ] = 100,
    offset: Annotated[int, Query(ge=0, description="Смещение")] = 0,
) -> ClubListResponse:
    """Получить все клубы с пагинацией"""
    dtos = await club_use_cases.get_all_clubs(limit=limit, offset=offset)
    return ClubListResponse(
        items=[response_mapper.to_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/search")
@inject
async def search_clubs(
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
    name: Annotated[
        str,
        Query(min_length=2, description="Название клуба для поиска"),
    ],
) -> list[ClubResponse]:
    """Поиск клубов по названию"""
    dtos = await club_use_cases.search_clubs(name=name)
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/{club_id}")
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


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_club(
    club_data: ClubCreate,
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
    _: Annotated[dict[str, object], Depends(require_permission(Permission.NSI_WRITE))],
) -> ClubResponse:
    """Создать новый клуб"""
    dto = CreateClubDTO(**club_data.model_dump())
    result_dto = await club_use_cases.create_club(dto)
    return response_mapper.to_response(result_dto)


@router.get("/league/{league_id}")
@inject
async def get_clubs_by_league(
    league_id: UUID,
    club_use_cases: FromDishka[ClubUseCases],
    response_mapper: FromDishka[IClubResponseMapper],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[ClubResponse]:
    """Получить клубы лиги"""
    dtos = await club_use_cases.get_clubs_by_league(league_id=league_id, limit=limit)
    return [response_mapper.to_response(dto) for dto in dtos]
