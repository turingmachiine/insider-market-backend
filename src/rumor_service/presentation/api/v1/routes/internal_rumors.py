from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.common.application.service_context import ServiceContext
from src.common.domain.service_auth import RUMOR_INGEST_SCOPE
from src.common.presentation.decorators import require_service_auth
from src.rumor_service.application.dto import CreateRawPublicationDTO, CreateRumorDTO
from src.rumor_service.application.usecases import RawPublicationUseCases, RumorUseCases
from src.rumor_service.presentation.api.v1.schemas import (
    RawPublicationCreate,
    RawPublicationResponse,
    RumorCreate,
    RumorResponse,
)

router = APIRouter(prefix="/internal", tags=["Internal Rumors"])


@router.post(
    "/raw-publications",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_publication(
    publication_data: RawPublicationCreate,
    raw_publication_use_cases: FromDishka[RawPublicationUseCases],
    _: Annotated[ServiceContext, Depends(require_service_auth(RUMOR_INGEST_SCOPE))],
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


@router.post(
    "/rumors",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_rumor(
    rumor_data: RumorCreate,
    rumor_use_cases: FromDishka[RumorUseCases],
    _: Annotated[ServiceContext, Depends(require_service_auth(RUMOR_INGEST_SCOPE))],
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
