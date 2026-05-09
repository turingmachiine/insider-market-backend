import pytest

from src.nsi_service.domain.services import PlayerService, TeamService


@pytest.fixture
def player_service() -> PlayerService:
    return PlayerService()


@pytest.fixture
def team_service() -> TeamService:
    return TeamService()
