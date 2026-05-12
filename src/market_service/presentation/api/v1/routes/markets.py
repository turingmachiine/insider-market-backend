from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.market_service.application.dto import (
    CreateMarketDTO,
    PlaceBetDTO,
    ResolveMarketDTO,
)
from src.market_service.application.usecases import MarketUseCases
from src.market_service.domain.entities import MarketStatus
from src.market_service.presentation.api.v1.schemas import (
    BetCreate,
    BetListResponse,
    BetResponse,
    MarketCreate,
    MarketListResponse,
    MarketResolve,
    MarketResponse,
    PositionListResponse,
    PositionResponse,
)

router = APIRouter(prefix="/markets", tags=["Markets"])


@router.get("")
@inject
async def get_markets(
    market_use_cases: FromDishka[MarketUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    status_filter: Annotated[MarketStatus | None, Query(alias="status")] = None,
    event_id: UUID | None = None,
) -> MarketListResponse:
    dtos = await market_use_cases.get_markets(
        limit=limit,
        offset=offset,
        status=status_filter,
        event_id=event_id,
    )
    return MarketListResponse(
        items=[MarketResponse(**dto.__dict__) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/{market_id}")
@inject
async def get_market(
    market_id: UUID,
    market_use_cases: FromDishka[MarketUseCases],
) -> MarketResponse:
    dto = await market_use_cases.get_market(market_id)
    if dto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {str(market_id)} not found",
        )
    return MarketResponse(**dto.__dict__)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_market(
    market_data: MarketCreate,
    market_use_cases: FromDishka[MarketUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.MARKET_WRITE))
    ],
) -> MarketResponse:
    market_payload = market_data.model_dump()
    market_payload["created_by_user_id"] = auth_payload.user_id
    dto = CreateMarketDTO(**market_payload)
    try:
        result = await market_use_cases.create_market(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return MarketResponse(**result.__dict__)


@router.post("/{market_id}/bets", status_code=status.HTTP_201_CREATED)
@inject
async def place_bet(
    market_id: UUID,
    bet_data: BetCreate,
    market_use_cases: FromDishka[MarketUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.MARKET_TRADE))
    ],
) -> BetResponse:
    bet_payload = bet_data.model_dump()
    bet_payload["user_id"] = auth_payload.user_id
    dto = PlaceBetDTO(**bet_payload)
    try:
        result = await market_use_cases.place_bet(market_id, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return BetResponse(**result.__dict__)


@router.get("/{market_id}/bets")
@inject
async def get_market_bets(
    market_id: UUID,
    market_use_cases: FromDishka[MarketUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.MARKET_READ))],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    user_id: UUID | None = None,
) -> BetListResponse:
    dtos = await market_use_cases.get_market_bets(
        market_id=market_id,
        limit=limit,
        offset=offset,
        user_id=user_id,
    )
    return BetListResponse(
        items=[BetResponse(**dto.__dict__) for dto in dtos],
        total=len(dtos),
        limit=limit,
        offset=offset,
    )


@router.get("/{market_id}/positions")
@inject
async def get_market_positions(
    market_id: UUID,
    market_use_cases: FromDishka[MarketUseCases],
) -> PositionListResponse:
    dtos = await market_use_cases.get_market_positions(market_id)
    return PositionListResponse(
        items=[PositionResponse(**dto.__dict__) for dto in dtos],
        total=len(dtos),
    )


@router.post("/{market_id}/close")
@inject
async def close_market(
    market_id: UUID,
    market_use_cases: FromDishka[MarketUseCases],
    _: Annotated[UserContext, Depends(require_permission(Permission.MARKET_MANAGE))],
) -> MarketResponse:
    try:
        result = await market_use_cases.close_market(market_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {str(market_id)} not found",
        )
    return MarketResponse(**result.__dict__)


@router.post("/{market_id}/resolve")
@inject
async def resolve_market(
    market_id: UUID,
    resolve_data: MarketResolve,
    market_use_cases: FromDishka[MarketUseCases],
    auth_payload: Annotated[
        UserContext, Depends(require_permission(Permission.MARKET_MANAGE))
    ],
) -> MarketResponse:
    resolve_payload = resolve_data.model_dump()
    resolve_payload["resolved_by_user_id"] = auth_payload.user_id
    dto = ResolveMarketDTO(**resolve_payload)
    try:
        result = await market_use_cases.resolve_market(market_id, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {str(market_id)} not found",
        )
    return MarketResponse(**result.__dict__)
