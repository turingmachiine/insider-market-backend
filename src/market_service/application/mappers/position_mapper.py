from abc import ABC, abstractmethod

from src.market_service.application.dto import PositionDTO
from src.market_service.domain.entities import Position


class IPositionMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(entity: Position) -> PositionDTO:
        pass


class PositionMapper(IPositionMapper):
    @staticmethod
    def to_dto(entity: Position) -> PositionDTO:
        return PositionDTO(
            id=entity.id,
            market_id=entity.market_id,
            user_id=entity.user_id,
            side=entity.side,
            shares=entity.shares,
            invested_amount=entity.invested_amount,
            realized_payout=entity.realized_payout,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
