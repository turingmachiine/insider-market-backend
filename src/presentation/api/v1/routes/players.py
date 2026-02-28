"""API endpoints для игроков"""

import logging
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from src.application.dto import CreatePlayerDTO, UpdatePlayerDTO
from src.application.usecases import PlayerUseCases
from src.presentation.api.v1.mappers import IPlayerResponseMapper
from src.presentation.api.v1.schemas import (
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


@router.get("", response_model=PlayerListResponse)
@inject
async def get_all_players(
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: int = Query(  # noqa: B008
        100, ge=1, le=500, description="Максимальное количество результатов"
    ),
    offset: int = Query(0, ge=0, description="Смещение"),  # noqa: B008
) -> PlayerListResponse:
    """Получить всех игроков с пагинацией"""
    dtos = await player_use_cases.get_all_players(limit=limit, offset=offset)
    return PlayerListResponse(
        items=[response_mapper.to_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=list[PlayerResponse])
@inject
async def search_players(
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    name: str = Query(  # noqa: B008
        ..., min_length=2, description="Имя игрока для поиска"
    ),
) -> list[PlayerResponse]:
    """Поиск игроков по имени"""
    dtos = await player_use_cases.search_players(name=name)
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/{player_id}", response_model=PlayerResponse)
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


@router.post("", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
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


@router.patch("/{player_id}", response_model=PlayerResponse)
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


@router.delete("/{player_id}", response_model=BaseResponse)
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


@router.get("/{player_id}/radar", response_model=PlayerRadarResponse)
@inject
async def get_player_radar(
    player_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    include_league_average: bool = Query(  # noqa: B008
        True, description="Включить средние значения по лиге"
    ),
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


@router.get("/{player_id}/similar", response_model=list[SimilarPlayerResponse])
@inject
async def find_similar_players(
    player_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    limit: int = Query(  # noqa: B008
        10, ge=1, le=50, description="Максимальное количество результатов"
    ),
    min_similarity: float = Query(  # noqa: B008
        0.7, ge=0.0, le=1.0, description="Минимальная схожесть"
    ),
    consider_league_strength: bool = Query(  # noqa: B008
        True, description="Учитывать силу лиги при подборе"
    ),
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


@router.get("/position/{position}", response_model=list[PlayerResponse])
@inject
async def get_players_by_position(
    position: str,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: int = Query(50, ge=1, le=200),  # noqa: B008
) -> list[PlayerResponse]:
    """Получить игроков по позиции"""
    dtos = await player_use_cases.get_players_by_position(
        position=position, limit=limit
    )
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/league/{league_id}", response_model=list[PlayerResponse])
@inject
async def get_players_by_league(
    league_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: int = Query(100, ge=1, le=500),  # noqa: B008
) -> list[PlayerResponse]:
    """Получить игроков лиги"""
    dtos = await player_use_cases.get_players_by_league(
        league_id=league_id, limit=limit
    )
    return [response_mapper.to_response(dto) for dto in dtos]


@router.get("/club/{club_id}", response_model=list[PlayerResponse])
@inject
async def get_players_by_club(
    club_id: UUID,
    player_use_cases: FromDishka[PlayerUseCases],
    response_mapper: FromDishka[IPlayerResponseMapper],
    limit: int = Query(50, ge=1, le=200),  # noqa: B008
) -> list[PlayerResponse]:
    """Получить игроков клуба"""
    dtos = await player_use_cases.get_players_by_club(club_id=club_id, limit=limit)
    return [response_mapper.to_response(dto) for dto in dtos]
