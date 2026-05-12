"""API endpoints для команд пользователей"""

import logging
from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.common.presentation.utils import can_access_user_resource, raise_forbidden
from src.nsi_service.application.constants import TEAM_ACCESS_DENIED_DETAIL
from src.nsi_service.application.dto import CreateTeamDTO
from src.nsi_service.application.usecases import TeamUseCases
from src.nsi_service.presentation.api.v1.mappers import ITeamResponseMapper
from src.nsi_service.presentation.api.v1.schemas import (
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
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.NSI_READ))
    ],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TeamListResponse:
    """Получить команды пользователя"""
    user_id = auth_payload.user_id

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
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.NSI_READ))
    ],
) -> TeamResponse:
    """Получить команду по ID"""
    dto = await team_use_cases.get_team(team_id)
    if not dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    if not can_access_user_resource(
        auth_payload, dto.user_id, Permission.TEAM_READ_ANY
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TEAM_ACCESS_DENIED_DETAIL,
        )
    return response_mapper.to_response(dto)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_team(
    team_data: TeamCreate,
    team_use_cases: FromDishka[TeamUseCases],
    response_mapper: FromDishka[ITeamResponseMapper],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.TEAM_WRITE))
    ],
) -> TeamResponse:
    """Создать новую команду"""
    user_id = auth_payload.user_id

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
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.TEAM_WRITE))
    ],
) -> TeamResponse:
    """Добавить игрока в команду"""
    try:
        dto = await team_use_cases.add_player_to_team(
            team_id=team_id,
            position=request.position,
            player_id=request.player_id,
            owner_user_id=auth_payload.user_id,
        )
    except PermissionError:
        raise_forbidden(TEAM_ACCESS_DENIED_DETAIL)
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
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.TEAM_WRITE))
    ],
    position: Annotated[str, Query(description="Позиция игрока")],
    player_id: Annotated[UUID, Query(description="ID игрока")],
) -> BaseResponse:
    """Удалить игрока из команды"""
    try:
        dto = await team_use_cases.remove_player_from_team(
            team_id=team_id,
            position=position,
            player_id=player_id,
            owner_user_id=auth_payload.user_id,
        )
    except PermissionError:
        raise_forbidden(TEAM_ACCESS_DENIED_DETAIL)
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
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.TEAM_WRITE))
    ],
) -> BaseResponse:
    """Удалить команду"""
    try:
        success = await team_use_cases.delete_by_id(
            team_id,
            owner_user_id=auth_payload.user_id,
        )
    except PermissionError:
        raise_forbidden(TEAM_ACCESS_DENIED_DETAIL)
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
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.TEAM_WRITE))
    ],
    budget: Annotated[
        float | None,
        Query(ge=0, description="Бюджет на трансферы"),
    ] = None,
) -> ShadowTeamResponse:
    """Построить shadow-team для усиления состава"""
    try:
        shadow_team = await team_use_cases.build_shadow_team(
            team_id=team_id,
            budget=budget,
            owner_user_id=auth_payload.user_id,
        )
    except PermissionError:
        raise_forbidden(TEAM_ACCESS_DENIED_DETAIL)
    if not shadow_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    return ShadowTeamResponse(**shadow_team.__dict__)
