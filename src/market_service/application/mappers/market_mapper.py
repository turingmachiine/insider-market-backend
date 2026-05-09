from abc import ABC, abstractmethod

from src.market_service.application.dto import MarketDTO
from src.market_service.domain.entities import Market


class IMarketMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(entity: Market) -> MarketDTO:
        pass


class MarketMapper(IMarketMapper):
    @staticmethod
    def to_dto(entity: Market) -> MarketDTO:
        return MarketDTO(
            id=entity.id,
            event_id=entity.event_id,
            title=entity.title,
            description=entity.description,
            initial_probability=entity.initial_probability,
            liquidity_parameter=entity.liquidity_parameter,
            yes_pool=entity.yes_pool,
            no_pool=entity.no_pool,
            yes_probability=entity.yes_probability,
            no_probability=entity.no_probability,
            yes_odds=entity.yes_odds,
            no_odds=entity.no_odds,
            status=entity.status,
            close_at=entity.close_at,
            outcome=entity.outcome,
            created_by_user_id=entity.created_by_user_id,
            resolved_by_user_id=entity.resolved_by_user_id,
            resolved_at=entity.resolved_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
