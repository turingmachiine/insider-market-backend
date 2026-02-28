import logging
from typing import Optional
from uuid import UUID

from src.application.dto import (
    CreatePlayerDTO,
    PlayerDTO,
    PlayerRadarDTO,
    SimilarPlayerDTO,
    UpdatePlayerDTO,
)
from src.application.mappers import (
    ICreatePlayerMapper,
    IPlayerMapper,
    IUpdatePlayerMapper,
)
from src.domain.interfaces.repositories import (
    IClubRepository,
    ILeagueRepository,
    IPlayerRepository,
)
from src.domain.value_objects.position import Position
from src.processing.matching.service import PlayerMatchingService
from src.processing.radar.service import RadarChartService

logger = logging.getLogger(__name__)


class PlayerUseCases:
    """Use cases для игроков"""

    def __init__(
        self,
        player_repository: IPlayerRepository,
        club_repository: IClubRepository,
        league_repository: ILeagueRepository,
        radar_service: RadarChartService,
        matching_service: PlayerMatchingService,
        player_mapper: IPlayerMapper,
        create_player_mapper: ICreatePlayerMapper,
        update_player_mapper: IUpdatePlayerMapper,
    ):
        self.player_repo = player_repository
        self.club_repo = club_repository
        self.league_repo = league_repository
        self.radar_service = radar_service
        self.matching_service = matching_service
        self.player_mapper = player_mapper
        self.create_mapper = create_player_mapper
        self.update_mapper = update_player_mapper

    async def get_player(self, player_id: UUID) -> Optional[PlayerDTO]:
        """Получить игрока по ID"""
        player = await self.player_repo.get_by_id(player_id)
        return self.player_mapper.to_dto(player) if player else None

    async def search_players(self, name: str) -> list[PlayerDTO]:
        """Поиск игроков по имени"""
        players = await self.player_repo.get_by_name(name)
        return [self.player_mapper.to_dto(p) for p in players]

    async def get_all_players(
        self, limit: int = 100, offset: int = 0
    ) -> list[PlayerDTO]:
        """Получить всех игроков с пагинацией"""
        players = await self.player_repo.get_all(limit=limit, offset=offset)
        return [self.player_mapper.to_dto(p) for p in players]

    async def get_players_by_position(
        self, position: str, limit: int = 50
    ) -> list[PlayerDTO]:
        """Получить игроков по позиции"""
        try:
            pos = Position(position)
        except ValueError:
            logger.warning(f"Invalid position: {position}")
            return []

        players = await self.player_repo.get_by_position(pos, limit=limit)
        return [self.player_mapper.to_dto(p) for p in players]

    async def get_players_by_league(
        self, league_id: UUID, limit: int = 100
    ) -> list[PlayerDTO]:
        """Получить игроков лиги"""
        players = await self.player_repo.get_by_league(league_id, limit=limit)
        return [self.player_mapper.to_dto(p) for p in players]

    async def get_players_by_club(
        self, club_id: UUID, limit: int = 50
    ) -> list[PlayerDTO]:
        """Получить игроков клуба"""
        players = await self.player_repo.get_by_club(club_id, limit=limit)
        return [self.player_mapper.to_dto(p) for p in players]

    async def create_player(self, dto: CreatePlayerDTO) -> PlayerDTO:
        """Создать нового игрока"""
        player = self.create_mapper.create_entity(dto)
        saved_player = await self.player_repo.save(player)
        return self.player_mapper.to_dto(saved_player)

    async def update_player(
        self, player_id: UUID, dto: UpdatePlayerDTO
    ) -> Optional[PlayerDTO]:
        """Обновить игрока"""
        player = await self.player_repo.get_by_id(player_id)
        if not player:
            return None

        updated_player = self.update_mapper.apply_to_entity(dto, player)
        saved_player = await self.player_repo.save(updated_player)
        return self.player_mapper.to_dto(saved_player)

    async def delete_player(self, player_id: UUID) -> bool:
        """Удалить игрока"""
        return await self.player_repo.delete_by_id(player_id)

    async def get_player_radar(
        self, player_id: UUID, include_league_average: bool = True
    ) -> Optional[PlayerRadarDTO]:
        """Получить данные для радар-чарта игрока"""
        player = await self.player_repo.get_by_id(player_id)
        if not player:
            return None

        return await self.radar_service.build_player_radar(
            player, include_league_average
        )

    async def find_similar_players(
        self,
        player_id: UUID,
        limit: int = 10,
        min_similarity: float = 0.7,
        consider_league_strength: bool = True,
    ) -> list[SimilarPlayerDTO]:
        """Найти похожих игроков"""
        player = await self.player_repo.get_by_id(player_id)
        if not player:
            return []

        all_players = await self.player_repo.get_all(limit=500)

        return self.matching_service.find_similar(
            target_player=player,
            candidates=all_players,
            limit=limit,
            min_similarity=min_similarity,
            consider_league_strength=consider_league_strength,
        )
