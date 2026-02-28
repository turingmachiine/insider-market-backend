"""Конфигурация pytest"""

import asyncio
from typing import Generator

import pytest

# Фикстуры для сущностей
from tests.fixtures.entities import (
    multiple_players,
    player_radar_metrics,
    sample_club,
    sample_league,
    sample_player,
    sample_team,
)
from tests.fixtures.services import player_service, team_service


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Создать event loop для сессии"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend() -> str:
    """Backend для anyio"""
    return "asyncio"


# Маркер для интеграционных тестов
def pytest_configure(config):
    """Настройка маркеров pytest"""
    config.addinivalue_line("markers", "integration: mark test as an integration test")


__all__ = [
    "multiple_players",
    "player_radar_metrics",
    "sample_club",
    "sample_league",
    "sample_player",
    "sample_team",
    "player_service",
    "team_service",
    "event_loop",
    "anyio_backend",
    "pytest_configure",
]
