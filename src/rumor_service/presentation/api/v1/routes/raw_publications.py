from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.rumor_service.application.dto import CreateRawPublicationDTO
from src.rumor_service.application.usecases import RawPublicationUseCases
from src.rumor_service.presentation.api.v1.schemas import (
    RawPublicationCreate,
    RawPublicationListResponse,
    RawPublicationResponse,
)

router = APIRouter(prefix="/raw-publications", tags=["Raw Publications"])


@router.get("/source/{source_id}")
@inject
async def get_publications_by_source(
    source_id: UUID,
    raw_publication_use_cases: FromDishka[RawPublicationUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RawPublicationListResponse:
    dtos = await raw_publication_use_cases.get_publications_by_source(
        source_id=source_id,
        limit=limit,
        offset=offset,
    )
    return RawPublicationListResponse(
        items=[RawPublicationResponse(**dto.__dict__) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/{publication_id}")
@inject
async def get_publication(
    publication_id: UUID,
    raw_publication_use_cases: FromDishka[RawPublicationUseCases],
) -> RawPublicationResponse:
    dto = await raw_publication_use_cases.get_publication(publication_id)
    if dto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Raw publication {str(publication_id)} not found",
        )
    return RawPublicationResponse(**dto.__dict__)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_publication(
    publication_data: RawPublicationCreate,
    raw_publication_use_cases: FromDishka[RawPublicationUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.RUMOR_WRITE))],
) -> RawPublicationResponse:
    dto = CreateRawPublicationDTO(**publication_data.model_dump())
    try:
        result = await raw_publication_use_cases.create_publication(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return RawPublicationResponse(**result.__dict__)
