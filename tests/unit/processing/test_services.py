"""Тесты для сервисов процессинга"""
import math

import pytest

from src.processing.matching.service import PlayerMatchingService
from src.processing.shadow_team.service import ShadowTeamService


class TestPlayerMatchingService:
    """Тесты для сервиса подбора игроков"""

    @pytest.fixture
    def matching_service(self) -> PlayerMatchingService:
        """Создать сервис подбора"""
        return PlayerMatchingService()

    def test_positions_compatible_same(
        self, matching_service: PlayerMatchingService
    ) -> None:
        """Тест совместимости одинаковых позиций"""
        from src.domain.value_objects.position import Position

        assert matching_service._positions_compatible(Position.ST, Position.ST) is True
        assert matching_service._positions_compatible(Position.CM, Position.CM) is True

    def test_positions_compatible_related(
        self, matching_service: PlayerMatchingService
    ) -> None:
        """Тест совместимости смежных позиций"""
        from src.domain.value_objects.position import Position

        # CDM и CM совместимы
        assert matching_service._positions_compatible(Position.CDM, Position.CM) is True

    def test_positions_not_compatible(
        self, matching_service: PlayerMatchingService
    ) -> None:
        """Тест несовместимых позиций"""
        from src.domain.value_objects.position import Position

        # GK и ST не совместимы
        assert matching_service._positions_compatible(Position.GK, Position.ST) is False

    def test_extract_features(
        self, matching_service: PlayerMatchingService, sample_player
    ) -> None:
        """Тест извлечения признаков"""
        features = matching_service._extract_features(sample_player)

        assert len(features) > 0
        assert all(isinstance(f, (int, float)) for f in features)


class TestShadowTeamService:
    """Тесты для сервиса shadow-team"""

    @pytest.fixture
    def shadow_service(self) -> ShadowTeamService:
        """Создать сервис shadow-team"""
        return ShadowTeamService()

    def test_calculate_player_rating(
        self, shadow_service: ShadowTeamService, sample_player
    ) -> None:
        """Тест расчета рейтинга для shadow-team"""
        rating = shadow_service._calculate_player_rating(sample_player)

        assert isinstance(rating, float)
        assert rating > 0

    def test_create_candidate_dto(
        self, shadow_service: ShadowTeamService, sample_player
    ) -> None:
        """Тест создания DTO кандидата"""
        candidate = shadow_service._create_candidate_dto(
            player=sample_player,
            improvement_score=0.25,
        )

        assert candidate.player_id == sample_player.id
        assert candidate.player_name == sample_player.name
        assert math.isclose(
            candidate.improvement_score, 0.25, rel_tol=1e-09, abs_tol=1e-09
        )
        assert "goals_per_90" in candidate.key_stats
