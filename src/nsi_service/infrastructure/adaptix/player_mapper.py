"""Реализация маппера Player с использованием adaptix"""

from datetime import date

from src.nsi_service.application.dto.player_dto import (
    CreatePlayerDTO,
    PlayerDTO,
    UpdatePlayerDTO,
)
from src.nsi_service.application.mappers import (
    ICreatePlayerMapper,
    IPlayerMapper,
    IUpdatePlayerMapper,
)
from src.nsi_service.domain.entities.player import Player
from src.nsi_service.domain.value_objects.position import Position


class PlayerMapperImpl(IPlayerMapper):
    """Реализация маппера Player с использованием adaptix"""

    def to_dto(self, entity: Player) -> PlayerDTO:
        """Конвертировать Player в PlayerDTO"""
        return PlayerDTO(
            id=entity.id,
            name=entity.name,
            first_name=entity.first_name,
            last_name=entity.last_name,
            date_of_birth=entity.date_of_birth,
            nationality=entity.nationality,
            position=entity.position.value,
            preferred_foot=entity.preferred_foot,
            height_cm=entity.height_cm,
            weight_kg=entity.weight_kg,
            current_club_id=entity.current_club_id,
            current_league_id=entity.current_league_id,
            market_value=entity.market_value,
            contract_until=entity.contract_until,
            shirt_number=entity.shirt_number,
            appearances=entity.appearances,
            goals=entity.goals,
            assists=entity.assists,
            minutes_played=entity.minutes_played,
            xg=entity.xg,
            xa=entity.xa,
            xg_per_90=entity.xg_per_90,
            xa_per_90=entity.xa_per_90,
            league_strength_coefficient=entity.league_strength_coefficient,
            age=entity.age,
        )

    def to_entity(self, dto: PlayerDTO) -> Player:
        """Конвертировать PlayerDTO в Player"""
        return Player(
            id=dto.id,
            name=dto.name,
            first_name=dto.first_name,
            last_name=dto.last_name,
            date_of_birth=dto.date_of_birth,
            nationality=dto.nationality,
            position=Position(dto.position),
            preferred_foot=dto.preferred_foot,
            height_cm=dto.height_cm,
            weight_kg=dto.weight_kg,
            current_club_id=dto.current_club_id,
            current_league_id=dto.current_league_id,
            market_value=dto.market_value,
            contract_until=dto.contract_until,
            shirt_number=dto.shirt_number,
            appearances=dto.appearances,
            goals=dto.goals,
            assists=dto.assists,
            minutes_played=dto.minutes_played,
            xg=dto.xg,
            xa=dto.xa,
            xg_per_90=dto.xg_per_90,
            xa_per_90=dto.xa_per_90,
            league_strength_coefficient=dto.league_strength_coefficient,
        )


class CreatePlayerMapperImpl(ICreatePlayerMapper):
    """Реализация маппера создания Player"""

    def create_entity(self, dto: CreatePlayerDTO) -> Player:
        """Создать Player из CreatePlayerDTO"""
        from uuid import uuid4

        return Player(
            id=uuid4(),
            name=dto.name,
            first_name=dto.first_name,
            last_name=dto.last_name,
            date_of_birth=dto.date_of_birth or date(2000, 1, 1),
            nationality=dto.nationality,
            position=Position(dto.position) if dto.position else Position.UNKNOWN,
            preferred_foot=dto.preferred_foot,
            height_cm=dto.height_cm,
            weight_kg=dto.weight_kg,
            current_club_id=dto.current_club_id,
            current_league_id=dto.current_league_id,
            market_value=dto.market_value,
            contract_until=dto.contract_until,
            shirt_number=dto.shirt_number,
        )


class UpdatePlayerMapperImpl(IUpdatePlayerMapper):
    """Реализация маппера обновления Player"""

    def apply_to_entity(self, dto: UpdatePlayerDTO, entity: Player) -> Player:
        """Применить UpdatePlayerDTO к Player"""
        if dto.name is not None:
            entity.name = dto.name
        if dto.first_name is not None:
            entity.first_name = dto.first_name
        if dto.last_name is not None:
            entity.last_name = dto.last_name
        if dto.date_of_birth is not None:
            entity.date_of_birth = dto.date_of_birth
        if dto.nationality is not None:
            entity.nationality = dto.nationality
        if dto.position is not None:
            entity.position = Position(dto.position)
        if dto.preferred_foot is not None:
            entity.preferred_foot = dto.preferred_foot
        if dto.height_cm is not None:
            entity.height_cm = dto.height_cm
        if dto.weight_kg is not None:
            entity.weight_kg = dto.weight_kg
        if dto.current_club_id is not None:
            entity.current_club_id = dto.current_club_id
        if dto.current_league_id is not None:
            entity.current_league_id = dto.current_league_id
        if dto.market_value is not None:
            entity.market_value = dto.market_value
        if dto.contract_until is not None:
            entity.contract_until = dto.contract_until
        if dto.shirt_number is not None:
            entity.shirt_number = dto.shirt_number
        return entity
