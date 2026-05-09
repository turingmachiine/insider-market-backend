"""Fixtures для тестов"""

from datetime import date
from decimal import Decimal
from typing import TypedDict
from uuid import uuid4

import pytest

from src.nsi_service.domain.entities.club import Club
from src.nsi_service.domain.entities.league import League
from src.nsi_service.domain.entities.player import Player
from src.nsi_service.domain.entities.team import Team
from src.nsi_service.domain.value_objects.position import Position


class PlayerFixtureData(TypedDict):
    name: str
    position: Position
    goals: int
    assists: int
    xg_per_90: float
    xa_per_90: float


@pytest.fixture
def sample_league() -> League:
    """Создать тестовую лигу"""
    return League(
        id=uuid4(),
        name="Premier League",
        short_name="EPL",
        country="England",
        tier=1,
        confederation="UEFA",
        logo_url="https://example.com/epl.png",
        strength_coefficient=1.0,
        current_season="2024/2025",
        season_start=date(2024, 8, 1),
        season_end=date(2025, 5, 31),
    )


@pytest.fixture
def sample_club(sample_league: League) -> Club:
    """Создать тестовый клуб"""
    return Club(
        id=uuid4(),
        name="Manchester City",
        short_name="Man City",
        founded_year=1880,
        country="England",
        city="Manchester",
        stadium_name="Etihad Stadium",
        stadium_capacity=55000,
        league_id=sample_league.id,
        logo_url="https://example.com/mancity.png",
        website="https://mancity.com",
        squad_market_value=Decimal("1000000000"),
        average_age=26.5,
        foreign_players_count=20,
        national_team_players_count=15,
    )


@pytest.fixture
def sample_player(sample_club: Club, sample_league: League) -> Player:
    """Создать тестового игрока"""
    return Player(
        id=uuid4(),
        name="Erling Haaland",
        first_name="Erling",
        last_name="Haaland",
        date_of_birth=date(2000, 7, 21),
        nationality="Norway",
        position=Position.ST,
        preferred_foot="left",
        height_cm=195,
        weight_kg=88,
        current_club_id=sample_club.id,
        current_league_id=sample_league.id,
        market_value=Decimal("180000000"),
        contract_until=date(2027, 6, 30),
        shirt_number=9,
        appearances=30,
        goals=25,
        assists=5,
        minutes_played=2500,
        xg=22.5,
        xa=4.2,
        xg_per_90=0.81,
        xa_per_90=0.15,
        league_strength_coefficient=1.0,
    )


@pytest.fixture
def sample_team() -> Team:
    """Создать тестовую команду пользователя"""
    return Team(
        id=uuid4(),
        name="My Dream Team",
        user_id=uuid4(),
        description="Test team",
        squad={
            Position.GK.value: [str(uuid4())],
            Position.CB.value: [str(uuid4()), str(uuid4())],
            Position.LB.value: [str(uuid4())],
            Position.RB.value: [str(uuid4())],
            Position.CDM.value: [str(uuid4())],
            Position.CM.value: [str(uuid4()), str(uuid4())],
            Position.LW.value: [str(uuid4())],
            Position.RW.value: [str(uuid4())],
            Position.ST.value: [str(uuid4())],
        },
    )


@pytest.fixture
def multiple_players(sample_club: Club, sample_league: League) -> list[Player]:
    """Создать несколько тестовых игроков"""
    players_data: list[PlayerFixtureData] = [
        {
            "name": "Kevin De Bruyne",
            "position": Position.CM,
            "goals": 8,
            "assists": 15,
            "xg_per_90": 0.25,
            "xa_per_90": 0.65,
        },
        {
            "name": "Phil Foden",
            "position": Position.LW,
            "goals": 15,
            "assists": 8,
            "xg_per_90": 0.55,
            "xa_per_90": 0.35,
        },
        {
            "name": "Rodri",
            "position": Position.CDM,
            "goals": 5,
            "assists": 7,
            "xg_per_90": 0.15,
            "xa_per_90": 0.25,
        },
        {
            "name": "Ruben Dias",
            "position": Position.CB,
            "goals": 2,
            "assists": 1,
            "xg_per_90": 0.05,
            "xa_per_90": 0.05,
        },
    ]

    players = []
    for data in players_data:
        player = Player(
            id=uuid4(),
            name=data["name"],
            first_name=data["name"].split()[0],
            last_name=data["name"].split()[-1],
            date_of_birth=date(1995, 1, 1),
            nationality="Various",
            position=data["position"],
            preferred_foot="right",
            height_cm=180,
            weight_kg=75,
            current_club_id=sample_club.id,
            current_league_id=sample_league.id,
            market_value=Decimal("50000000"),
            contract_until=date(2026, 6, 30),
            shirt_number=10,
            appearances=30,
            goals=data["goals"],
            assists=data["assists"],
            minutes_played=2500,
            xg=data["goals"] * 0.9,
            xa=data["assists"] * 0.8,
            xg_per_90=data["xg_per_90"],
            xa_per_90=data["xa_per_90"],
            league_strength_coefficient=1.0,
        )
        players.append(player)

    return players


@pytest.fixture
def player_radar_metrics() -> dict:
    """Метрики для радар-чарта"""
    return {
        "goals_per_90": 0.75,
        "assists_per_90": 0.25,
        "xg_per_90": 0.68,
        "xa_per_90": 0.20,
        "shots_per_90": 4.5,
        "dribbles_completed_per_90": 1.2,
        "aerial_duels_won_pct": 55.0,
        "touches_in_box_per_90": 8.5,
    }
