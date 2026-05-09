"""API endpoints для игроков"""

import logging
from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from src.nsi_service.application.dto import CreatePlayerDTO, UpdatePlayerDTO
from src.nsi_service.application.usecases import PlayerUseCases
from src.nsi_service.presentation.api.v1.mappers import IPlayerResponseMapper
from src.nsi_service.presentation.api.v1.schemas import (
    BaseResponse,
    PlayerCreate,
    PlayerListResponse,
    PlayerRadarResponse,
    PlayerResponse,
    PlayerUpdate,
    SimilarPlayerResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("")
@inject
async def get_all_players(
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: Annotated[
        int,
        Query(ge=1, le=500, description="Максимальное количество результатов"),
    ] = 100,
    offset: Annotated[int, Query(ge=0, description="Смещение")] = 0,
) -> PlayerListResponse:
    """Получить всех игроков с пагинацией"""
    dtos = await player_use_cases.get_all_players(limit=limit, offset=offset)
    return PlayerListResponse(
        items=[response_mapper.to_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/search")
@inject
async def search_players(
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    name: Annotated[
        str,
        Query(min_length=2, description="Имя игрока для поиска"),
    ],
) -> list[PlayerResponse]:
    """Поиск игроков по имени"""
    dtos = await player_use_cases.search_players(name=name)
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/{player_id}")
@inject
async def get_player(
    player_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
) -> PlayerResponse:
    """Получить игрока по ID"""
    dto = await player_use_cases.get_player(player_id)
    if not dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )
    return response_mapper.to_response(dto)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_player(
    player_data: PlayerCreate,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
) -> PlayerResponse:
    """Создать нового игрока"""
    dto = CreatePlayerDTO(**player_data.model_dump())
    result_dto = await player_use_cases.create_player(dto)
    return response_mapper.to_response(result_dto)


@router.patch("/{player_id}")
@inject
async def update_player(
    player_id: UUID,
    player_data: PlayerUpdate,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
) -> PlayerResponse:
    """Обновить игрока"""
    dto = UpdatePlayerDTO(**player_data.model_dump(exclude_unset=True))
    result_dto = await player_use_cases.update_player(player_id, dto)
    if not result_dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )
    return response_mapper.to_response(result_dto)


@router.delete("/{player_id}")
@inject
async def delete_player(
    player_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
) -> BaseResponse:
    """Удалить игрока"""
    success = await player_use_cases.delete_player(player_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )
    return BaseResponse(message="Player deleted successfully")


@router.get("/{player_id}/radar")
@inject
async def get_player_radar(
    player_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    include_league_average: Annotated[
        bool,
        Query(description="Включить средние значения по лиге"),
    ] = True,
) -> PlayerRadarResponse:
    """Получить данные для радар-чарта игрока"""
    radar = await player_use_cases.get_player_radar(
        player_id, include_league_average=include_league_average
    )
    if not radar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )
    return PlayerRadarResponse(**radar.__dict__)


@router.get("/{player_id}/similar")
@inject
async def find_similar_players(
    player_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    limit: Annotated[
        int,
        Query(ge=1, le=50, description="Максимальное количество результатов"),
    ] = 10,
    min_similarity: Annotated[
        float,
        Query(ge=0.0, le=1.0, description="Минимальная схожесть"),
    ] = 0.7,
    consider_league_strength: Annotated[
        bool,
        Query(description="Учитывать силу лиги при подборе"),
    ] = True,
) -> list[SimilarPlayerResponse]:
    """Найти похожих игроков"""
    similar_players = await player_use_cases.find_similar_players(
        player_id=player_id,
        limit=limit,
        min_similarity=min_similarity,
        consider_league_strength=consider_league_strength,
    )
    return [
        SimilarPlayerResponse(**similar_player.__dict__)
        for similar_player in similar_players
    ]


@router.get("/position/{position}")
@inject
async def get_players_by_position(
    position: str,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[PlayerResponse]:
    """Получить игроков по позиции"""
    dtos = await player_use_cases.get_players_by_position(
        position=position, limit=limit
    )
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/league/{league_id}")
@inject
async def get_players_by_league(
    league_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[PlayerResponse]:
    """Получить игроков лиги"""
    dtos = await player_use_cases.get_players_by_league(
        league_id=league_id, limit=limit
    )
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/club/{club_id}")
@inject
async def get_players_by_club(
    club_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[PlayerResponse]:
    """Получить игроков клуба"""
    dtos = await player_use_cases.get_players_by_club(club_id=club_id, limit=limit)
    return [response_mapper.to_response(dto) for dto in dtos]
