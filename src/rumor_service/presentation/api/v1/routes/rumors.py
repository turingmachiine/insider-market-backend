from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.rumor_service.application.dto import CreateRumorDTO, UpdateRumorStatusDTO
from src.rumor_service.application.usecases import RumorUseCases, SourceUseCases
from src.rumor_service.domain.entities import RumorStatus
from src.rumor_service.presentation.api.v1.schemas import (
    PublicRumorListResponse,
    PublicRumorResponse,
    RumorCreate,
    RumorListResponse,
    RumorResponse,
    RumorStatusUpdate,
)

router = APIRouter(prefix="/rumors", tags=["Rumors"])


@router.get("")
@inject
async def get_rumors(
    rumor_use_cases: FromDishka[RumorUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    status_filter: Annotated[RumorStatus | None, Query(alias="status")] = None,
    source_id: UUID | None = None,
    event_id: UUID | None = None,
    is_public: bool | None = None,
) -> RumorListResponse:
    dtos = await rumor_use_cases.get_rumors(
        limit=limit,
        offset=offset,
        status=status_filter,
        source_id=source_id,
        event_id=event_id,
        is_public=is_public,
    )
    return RumorListResponse(
        items=[RumorResponse(**dto.__dict__) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/public")
@inject
async def get_public_rumors(
    rumor_use_cases: FromDishka[RumorUseCases],
    source_use_cases: FromDishka[SourceUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    event_id: UUID | None = None,
) -> PublicRumorListResponse:
    dtos = await rumor_use_cases.get_rumors(
        limit=limit,
        offset=offset,
        event_id=event_id,
        is_public=True,
    )
    items: list[PublicRumorResponse] = []
    for dto in dtos:
        source = await source_use_cases.get_source(dto.source_id)
        items.append(
            PublicRumorResponse(
                rumor=RumorResponse(**dto.__dict__),
                source=source.__dict__ if source is not None else None,
            )
        )
    return PublicRumorListResponse(
        items=items,
        total=len(items),
        limit=limit,
        offset=offset,
    )


@router.get("/{rumor_id}")
@inject
async def get_rumor(
    rumor_id: UUID,
    rumor_use_cases: FromDishka[RumorUseCases],
) -> RumorResponse:
    dto = await rumor_use_cases.get_rumor(rumor_id)
    if dto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rumor {str(rumor_id)} not found",
        )
    return RumorResponse(**dto.__dict__)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_rumor(
    rumor_data: RumorCreate,
    rumor_use_cases: FromDishka[RumorUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RUMOR_WRITE))],
) -> RumorResponse:
    dto = CreateRumorDTO(**rumor_data.model_dump())
    try:
        result = await rumor_use_cases.create_rumor(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return RumorResponse(**result.__dict__)


@router.patch("/{rumor_id}/status")
@inject
async def update_rumor_status(
    rumor_id: UUID,
    status_data: RumorStatusUpdate,
    rumor_use_cases: FromDishka[RumorUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RUMOR_MODERATE))],
) -> RumorResponse:
    dto = UpdateRumorStatusDTO(**status_data.model_dump())
    result = await rumor_use_cases.update_status(rumor_id, dto)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rumor {str(rumor_id)} not found",
        )
    return RumorResponse(**result.__dict__)
