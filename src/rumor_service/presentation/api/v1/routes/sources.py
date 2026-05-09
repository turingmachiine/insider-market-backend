from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from src.rumor_service.application.dto import CreateSourceDTO
from src.rumor_service.application.usecases import SourceUseCases
from src.rumor_service.presentation.api.v1.schemas import (
    SourceCreate,
    SourceListResponse,
    SourceResponse,
)

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("")
@inject
async def get_sources(
    source_use_cases: FromDishka[SourceUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    active_only: bool = False,
) -> SourceListResponse:
    dtos = await source_use_cases.get_sources(
        limit=limit,
        offset=offset,
        active_only=active_only,
    )
    return SourceListResponse(
        items=[SourceResponse(**dto.__dict__) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/{source_id}")
@inject
async def get_source(
    source_id: UUID,
    source_use_cases: FromDishka[SourceUseCases],
) -> SourceResponse:
    dto = await source_use_cases.get_source(source_id)
    if dto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {str(source_id)} not found",
        )
    return SourceResponse(**dto.__dict__)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_source(
    source_data: SourceCreate,
    source_use_cases: FromDishka[SourceUseCases],
) -> SourceResponse:
    dto = CreateSourceDTO(**source_data.model_dump())
    result = await source_use_cases.create_source(dto)
    return SourceResponse(**result.__dict__)
