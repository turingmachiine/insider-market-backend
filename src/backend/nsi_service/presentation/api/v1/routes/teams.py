"""API endpoints для команд пользователей"""

import logging
from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Header, HTTPException, Query, status

from src.backend.nsi_service.application.dto import CreateTeamDTO
from src.backend.nsi_service.application.usecases import TeamUseCases
from src.backend.nsi_service.presentation.api.v1.mappers import ITeamResponseMapper
from src.backend.nsi_service.presentation.api.v1.schemas import (
    AddPlayerToTeamRequest,
    BaseResponse,
    ShadowTeamResponse,
    TeamCreate,
    TeamListResponse,
    TeamResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("")
@inject
async def get_user_teams(
    team_use_cases: FromDishka[TeamUseCases],
    response_mapper: FromDishka[ITeamResponseMapper],
    x_user_id: Annotated[str, Header(description="ID пользователя")],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TeamListResponse:
    """Получить команды пользователя"""
    try:
        user_id = UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    dtos = await team_use_cases.get_user_teams(user_id)
    return TeamListResponse(
        items=[response_mapper.to_response(dto) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/{team_id}")
@inject
async def get_team(
    team_id: UUID,
    team_use_cases: FromDishka[TeamUseCases],
    response_mapper: FromDishka[ITeamResponseMapper],
) -> TeamResponse:
    """Получить команду по ID"""
    dto = await team_use_cases.get_team(team_id)
    if not dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    return response_mapper.to_response(dto)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_team(
    team_data: TeamCreate,
    team_use_cases: FromDishka[TeamUseCases],
    response_mapper: FromDishka[ITeamResponseMapper],
    x_user_id: Annotated[str, Header(description="ID пользователя")],
) -> TeamResponse:
    """Создать новую команду"""
    try:
        user_id = UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    dto = CreateTeamDTO(
        name=team_data.name,
        user_id=user_id,
        description=team_data.description,
    )
    result_dto = await team_use_cases.create_team(
        name=dto.name,
        user_id=dto.user_id,
        description=dto.description,
    )
    return response_mapper.to_response(result_dto)


@router.post("/{team_id}/players")
@inject
async def add_player_to_team(
    team_id: UUID,
    request: AddPlayerToTeamRequest,
    team_use_cases: FromDishka[TeamUseCases],
    response_mapper: FromDishka[ITeamResponseMapper],
) -> TeamResponse:
    """Добавить игрока в команду"""
    dto = await team_use_cases.add_player_to_team(
        team_id=team_id,
        position=request.position,
        player_id=request.player_id,
    )
    if not dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    return response_mapper.to_response(dto)


@router.delete("/{team_id}/players")
@inject
async def remove_player_from_team(
    team_id: UUID,
    team_use_cases: FromDishka[TeamUseCases],
    position: Annotated[str, Query(description="Позиция игрока")],
    player_id: Annotated[UUID, Query(description="ID игрока")],
) -> BaseResponse:
    """Удалить игрока из команды"""
    dto = await team_use_cases.remove_player_from_team(
        team_id=team_id,
        position=position,
        player_id=player_id,
    )
    if not dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    return BaseResponse(message="Player removed from team")


@router.delete("/{team_id}")
@inject
async def delete_team(
    team_id: UUID,
    team_use_cases: FromDishka[TeamUseCases],
) -> BaseResponse:
    """Удалить команду"""
    success = await team_use_cases.delete_by_id(team_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    return BaseResponse(message="Team deleted successfully")


@router.post("/{team_id}/shadow-team")
@inject
async def build_shadow_team(
    team_id: UUID,
    team_use_cases: FromDishka[TeamUseCases],
    budget: Annotated[
        float | None,
        Query(ge=0, description="Бюджет на трансферы"),
    ] = None,
) -> ShadowTeamResponse:
    """Построить shadow-team для усиления состава"""
    shadow_team = await team_use_cases.build_shadow_team(
        team_id=team_id,
        budget=budget,
    )
    if not shadow_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    return ShadowTeamResponse(**shadow_team.__dict__)
