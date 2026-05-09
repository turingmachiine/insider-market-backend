"""Use Cases приложения"""

import logging
from typing import Optional
from uuid import UUID

from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager
from src.nsi_service.application.dto import ShadowTeamDTO, TeamDTO
from src.nsi_service.application.mappers import ITeamMapper
from src.nsi_service.domain.interfaces.repositories import (
    IPlayerRepository,
    ITeamRepository,
)
from src.nsi_service.domain.services import TeamService
from src.nsi_service.processing.shadow_team.service import ShadowTeamService

logger = logging.getLogger(__name__)


@use_case
class TeamUseCases(HasTransactionManager):
    """Use cases для команд пользователей"""

    team_repository: ITeamRepository
    player_repository: IPlayerRepository
    shadow_team_service: ShadowTeamService
    team_service: TeamService
    team_mapper: ITeamMapper
    transaction_manager: TransactionManager

    async def get_team(self, team_id: UUID) -> Optional[TeamDTO]:
        """Получить команду по ID"""
        team = await self.team_repository.get_by_id(team_id)
        return self.team_mapper.to_dto(team) if team else None

    async def get_user_teams(self, user_id: UUID) -> list[TeamDTO]:
        """Получить команды пользователя"""
        teams = await self.team_repository.get_by_user(user_id)
        return [self.team_mapper.to_dto(t) for t in teams]

    @transactional()
    async def create_team(
        self, name: str, user_id: UUID, description: Optional[str] = None
    ) -> TeamDTO:
        """Создать новую команду"""
        from uuid import uuid4

        from src.nsi_service.domain.entities.team import Team

        team = Team(
            id=uuid4(),
            name=name,
            user_id=user_id,
            description=description,
            squad={},
        )

        saved_team = await self.team_repository.save(team)
        return self.team_mapper.to_dto(saved_team)

    @transactional()
    async def add_player_to_team(
        self, team_id: UUID, position: str, player_id: UUID
    ) -> Optional[TeamDTO]:
        """Добавить игрока в команду"""
        team = await self.team_repository.get_by_id(team_id)
        if not team:
            return None

        updated_team = self.team_service.add_player(team, position, player_id)
        saved_team = await self.team_repository.save(updated_team)
        return self.team_mapper.to_dto(saved_team)

    @transactional()
    async def remove_player_from_team(
        self, team_id: UUID, position: str, player_id: UUID
    ) -> Optional[TeamDTO]:
        """Удалить игрока из команды"""
        team = await self.team_repository.get_by_id(team_id)
        if not team:
            return None

        updated_team = self.team_service.remove_player(team, position, player_id)
        saved_team = await self.team_repository.save(updated_team)
        return self.team_mapper.to_dto(saved_team)

    @transactional()
    async def build_shadow_team(
        self, team_id: UUID, budget: Optional[float] = None
    ) -> Optional[ShadowTeamDTO]:
        """Построить shadow-team для усиления состава"""
        team = await self.team_repository.get_by_id(team_id)
        if not team:
            return None

        # Получение всех игроков для сравнения
        all_players = await self.player_repository.get_all(limit=1000)

        return self.shadow_team_service.build_shadow_team(
            user_team=team,
            all_players=all_players,
            budget=budget,
        )

    async def delete_by_id(self, team_id: UUID) -> bool:
        return await self.team_repository.delete_by_id(team_id)
