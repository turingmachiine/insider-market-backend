from uuid import UUID, uuid4

import pytest

from src.common.domain.interfaces import TransactionManager
from src.nsi_service.application.constants import TEAM_ACCESS_DENIED_DETAIL
from src.nsi_service.application.dto import TeamDTO
from src.nsi_service.application.mappers import ITeamMapper
from src.nsi_service.application.usecases.team_use_cases import TeamUseCases
from src.nsi_service.domain.entities import Player, Team
from src.nsi_service.domain.interfaces.repositories import (
    IPlayerRepository,
    ITeamRepository,
)
from src.nsi_service.domain.services import TeamService
from src.nsi_service.domain.value_objects import Position
from src.nsi_service.processing.shadow_team.service import ShadowTeamService


class FakeTransactionManager(TransactionManager):
    def __init__(self) -> None:
        self.started = 0
        self.committed = 0
        self.rolled_back = 0

    async def begin(self) -> None:
        self.started += 1

    async def begin_nested(self) -> None:
        self.started += 1

    async def commit(self) -> None:
        self.committed += 1

    async def rollback(self) -> None:
        self.rolled_back += 1

    async def flush(self) -> None:  # NOSONAR(S1186)
        pass

    @property
    def in_transaction(self) -> bool:
        return self.started > self.committed + self.rolled_back

    @property
    def in_nested(self) -> bool:
        return False


class FakeTeamRepository(ITeamRepository):
    def __init__(self, team: Team) -> None:
        self.teams = {team.id: team}
        self.saved: list[Team] = []
        self.deleted: list[Team] = []

    async def get_by_id(self, team_id: UUID) -> Team | None:  # NOSONAR(S7503)
        return self.teams.get(team_id)

    async def get_by_user(self, user_id: UUID) -> list[Team]:  # NOSONAR(S7503)
        return [team for team in self.teams.values() if team.user_id == user_id]

    async def save(self, team: Team) -> Team:  # NOSONAR(S7503)
        self.teams[team.id] = team
        self.saved.append(team)
        return team

    async def delete(self, team: Team) -> bool:  # NOSONAR(S7503)
        self.deleted.append(team)
        self.teams.pop(team.id, None)
        return True

    async def delete_by_id(self, team_id: UUID) -> bool:  # NOSONAR(S7503)
        team = self.teams.get(team_id)
        if team is None:
            return False
        return await self.delete(team)


class FakePlayerRepository(IPlayerRepository):
    async def get_by_id(self, player_id: UUID) -> Player | None:  # NOSONAR(S7503)
        return None

    async def get_by_name(self, name: str) -> list[Player]:  # NOSONAR(S7503)
        return []

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Player]:  # NOSONAR(S7503)
        return []

    async def get_by_position(
        self,
        position: Position,
        limit: int = 50,
    ) -> list[Player]:  # NOSONAR(S7503)
        return []

    async def get_by_league(
        self,
        league_id: UUID,
        limit: int = 100,
    ) -> list[Player]:  # NOSONAR(S7503)
        return []

    async def get_by_club(
        self,
        club_id: UUID,
        limit: int = 50,
    ) -> list[Player]:  # NOSONAR(S7503)
        return []

    async def save(self, player: Player) -> Player:  # NOSONAR(S7503)
        return player

    async def delete(self, player: Player) -> bool:  # NOSONAR(S7503)
        return True

    async def delete_by_id(self, player_id: UUID) -> bool:  # NOSONAR(S7503)
        return True


class FakeTeamMapper(ITeamMapper):
    def to_dto(self, entity: Team) -> TeamDTO:
        return TeamDTO(
            id=entity.id,
            name=entity.name,
            user_id=entity.user_id,
            description=entity.description,
            squad=entity.squad,
            player_count=sum(len(players) for players in entity.squad.values()),
        )

    def to_entity(self, dto: TeamDTO) -> Team:
        return Team(
            id=dto.id,
            name=dto.name,
            user_id=dto.user_id,
            description=dto.description,
            squad=dto.squad,
        )


def make_use_cases(team: Team) -> tuple[TeamUseCases, FakeTeamRepository]:
    repository = FakeTeamRepository(team)
    use_cases = TeamUseCases(
        team_repository=repository,
        player_repository=FakePlayerRepository(),
        shadow_team_service=ShadowTeamService(),
        team_service=TeamService(),
        team_mapper=FakeTeamMapper(),
        transaction_manager=FakeTransactionManager(),
    )
    return use_cases, repository


@pytest.mark.asyncio
async def test_add_player_to_team_rejects_non_owner() -> None:
    owner_id = uuid4()
    team = Team(id=uuid4(), name="Owner Team", user_id=owner_id)
    use_cases, repository = make_use_cases(team)

    with pytest.raises(PermissionError, match=TEAM_ACCESS_DENIED_DETAIL):
        await use_cases.add_player_to_team(
            team_id=team.id,
            position="striker",
            player_id=uuid4(),
            owner_user_id=uuid4(),
        )

    assert repository.saved == []


@pytest.mark.asyncio
async def test_add_player_to_team_allows_owner() -> None:
    owner_id = uuid4()
    player_id = uuid4()
    team = Team(id=uuid4(), name="Owner Team", user_id=owner_id)
    use_cases, repository = make_use_cases(team)

    dto = await use_cases.add_player_to_team(
        team_id=team.id,
        position="striker",
        player_id=player_id,
        owner_user_id=owner_id,
    )

    assert dto is not None
    assert str(player_id) in dto.squad["striker"]
    assert repository.saved == [team]


@pytest.mark.asyncio
async def test_delete_by_id_rejects_non_owner() -> None:
    owner_id = uuid4()
    team = Team(id=uuid4(), name="Owner Team", user_id=owner_id)
    use_cases, repository = make_use_cases(team)

    with pytest.raises(PermissionError, match=TEAM_ACCESS_DENIED_DETAIL):
        await use_cases.delete_by_id(team.id, owner_user_id=uuid4())

    assert repository.deleted == []
    assert repository.teams[team.id] == team
