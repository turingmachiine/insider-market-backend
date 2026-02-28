import pytest

from src.domain.services import PlayerService, TeamService


@pytest.fixture
def player_service() -> PlayerService:
    return PlayerService()


@pytest.fixture
def team_service() -> TeamService:
    return TeamService()
