from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.application.dto import PlayerDTO, PlayerRadarDTO, SimilarPlayerDTO


class IPlayerService(ABC):
    """Интерфейс сервиса игроков"""

    @abstractmethod
    async def get_player(self, player_id: UUID) -> Optional[PlayerDTO]:
        """Получить игрока по ID"""
        pass

    @abstractmethod
    async def search_players(self, name: str) -> list[PlayerDTO]:
        """Поиск игроков по имени"""
        pass

    @abstractmethod
    async def get_player_radar(
        self, player_id: UUID, include_league_average: bool = True
    ) -> Optional[PlayerRadarDTO]:
        """Получить данные для радар-чарта игрока"""
        pass

    @abstractmethod
    async def find_similar_players(
        self,
        player_id: UUID,
        limit: int = 10,
        min_similarity: float = 0.7,
    ) -> list[SimilarPlayerDTO]:
        """Найти похожих игроков"""
        pass
