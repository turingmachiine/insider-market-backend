"""Конфигурация pytest"""

import asyncio
from typing import Generator

import pytest

pytest_plugins = [
    "tests.fixtures.shared.entities",
    "tests.fixtures.shared.services",
]


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
