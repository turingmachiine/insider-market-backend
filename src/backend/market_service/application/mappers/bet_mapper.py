from abc import ABC, abstractmethod

from src.backend.market_service.application.dto import BetDTO
from src.backend.market_service.domain.entities import Bet


class IBetMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(entity: Bet) -> BetDTO:
        pass


class BetMapper(IBetMapper):
    @staticmethod
    def to_dto(entity: Bet) -> BetDTO:
        return BetDTO(
            id=entity.id,
            market_id=entity.market_id,
            user_id=entity.user_id,
            side=entity.side,
            amount=entity.amount,
            shares=entity.shares,
            probability_before=entity.probability_before,
            probability_after=entity.probability_after,
            odds_before=entity.odds_before,
            odds_after=entity.odds_after,
            created_at=entity.created_at,
        )
