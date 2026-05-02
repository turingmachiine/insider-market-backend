"""Сервис для подбора похожих игроков"""

import logging

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from src.backend.nsi_service.application.dto import SimilarPlayerDTO
from src.backend.nsi_service.domain.entities.player import Player
from src.backend.nsi_service.domain.value_objects.position import Position

logger = logging.getLogger(__name__)


# Веса для различных характеристик при сравнении
FEATURE_WEIGHTS = {
    # Физические характеристики
    "age": 0.05,
    "height_cm": 0.03,
    "weight_kg": 0.02,
    # Игровые статы (нормализованные на 90 минут)
    "goals_per_90": 0.15,
    "assists_per_90": 0.12,
    "xg_per_90": 0.10,
    "xa_per_90": 0.08,
    # Позиционно-зависимые статы
    "defensive_actions": 0.10,  # tackles + interceptions
    "progressive_actions": 0.10,  # progressive passes/carries
    "dribbling": 0.08,
    "aerial_ability": 0.05,
    # Сила лиги
    "league_strength": 0.12,
}


class PlayerMatchingService:
    """Сервис для подбора похожих игроков"""

    def __init__(self) -> None:
        self.scaler = StandardScaler()

    def find_similar(
        self,
        target_player: Player,
        candidates: list[Player],
        limit: int = 10,
        min_similarity: float = 0.7,
        consider_league_strength: bool = True,
    ) -> list[SimilarPlayerDTO]:
        """
        Найти похожих игроков.

        Args:
            target_player: Игрок, для которого ищем похожих
            candidates: Список кандидатов для сравнения
            limit: Максимальное количество результатов
            min_similarity: Минимальный порог схожести
            consider_league_strength: Учитывать силу лиги

        Returns:
            Список похожих игроков с score схожести
        """
        # Фильтрация кандидатов
        filtered_candidates = self._filter_candidates(
            target_player,
            candidates,
            consider_league_strength,
        )

        if not filtered_candidates:
            return []

        # Извлечение признаков
        target_features = self._extract_features(target_player)
        candidate_features = [
            self._extract_features(player) for player in filtered_candidates
        ]

        # Нормализация признаков
        all_features = [target_features] + candidate_features
        try:
            normalized_features = self.scaler.fit_transform(all_features)
        except ValueError:
            # Если недостаточно данных для нормализации
            normalized_features = np.array(all_features)

        target_normalized = normalized_features[0:1]
        candidates_normalized = normalized_features[1:]

        # Расчет схожести (косинусное сходство)
        similarities = cosine_similarity(target_normalized, candidates_normalized)[0]

        # Сортировка и фильтрация по порогу
        results = []
        for idx, similarity in enumerate(similarities):
            if similarity >= min_similarity:
                candidate = filtered_candidates[idx]
                similar_player = self._create_similar_player_dto(
                    candidate=candidate,
                    similarity_score=float(similarity),
                    target_player=target_player,
                )
                results.append(similar_player)

        # Сортировка по схожести и ограничение количества
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:limit]

    def _filter_candidates(
        self,
        target: Player,
        candidates: list[Player],
        consider_league_strength: bool,
    ) -> list[Player]:
        """Отфильтровать подходящих кандидатов"""
        filtered = []

        for candidate in candidates:
            # Исключаем самого игрока
            if candidate.id == target.id:
                continue

            # Та же позиция (или совместимая)
            if not self._positions_compatible(target.position, candidate.position):
                continue

            # Возраст в разумном диапазоне (±5 лет)
            if abs(candidate.age - target.age) > 5:
                continue

            # Сила лиги (если учитываем)
            if consider_league_strength:
                # Разница в коэффициенте силы лиги не более 0.3
                if (
                    abs(
                        candidate.league_strength_coefficient
                        - target.league_strength_coefficient
                    )
                    > 0.3
                ):
                    continue

            filtered.append(candidate)

        return filtered

    def _positions_compatible(self, pos1: Position, pos2: Position) -> bool:
        """Проверить совместимость позиций"""
        # Точное совпадение
        if pos1 == pos2:
            return True

        # Совместимые позиции
        compatible_groups = {
            # Защитники
            (Position.CB, Position.CB),
            (Position.LB, Position.RB),
            # Полузащитники
            (Position.CM, Position.CDM, Position.CAM),
            (Position.LW, Position.RW),
            # Нападающие
            (Position.ST,),
            # Вратари
            (Position.GK,),
        }

        # Проверяем, находятся ли позиции в одной группе
        pos1_value = pos1.value
        pos2_value = pos2.value

        for group in compatible_groups:
            if pos1_value in group and pos2_value in group:
                return True

        # Кросс-позиционная совместимость
        cross_compatible = {
            Position.CDM: [Position.CM, Position.CB],
            Position.CM: [Position.CDM, Position.CAM],
            Position.CAM: [Position.CM, Position.LW, Position.RW],
            Position.LW: [Position.CAM, Position.LB],
            Position.RW: [Position.CAM, Position.RB],
            Position.LB: [Position.LW, Position.CB],
            Position.RB: [Position.RW, Position.CB],
        }

        return pos2 in cross_compatible.get(pos1, [])

    def _extract_features(self, player: Player) -> np.ndarray:
        """Извлечь признаки игрока для сравнения"""
        minutes_factor = (
            90.0 / player.minutes_played if player.minutes_played > 0 else 0
        )

        features = {
            "age": player.age / 35.0,  # Нормализация
            "height_cm": player.height_cm / 200.0,
            "weight_kg": player.weight_kg / 100.0,
            "goals_per_90": (player.goals * minutes_factor) if minutes_factor else 0,
            "assists_per_90": (
                (player.assists * minutes_factor) if minutes_factor else 0
            ),
            "xg_per_90": player.xg_per_90,
            "xa_per_90": player.xa_per_90,
            "defensive_actions": self._calculate_defensive_actions(
                player, minutes_factor
            ),
            "progressive_actions": self._estimate_progressive_actions(player),
            "dribbling": self._estimate_dribbling(player),
            "aerial_ability": self._calculate_aerial_ability(player),
            "league_strength": player.league_strength_coefficient,
        }

        # Применение весов
        weighted_features = [
            features[feature] * FEATURE_WEIGHTS.get(feature, 1.0)
            for feature in features
        ]

        return np.array(weighted_features)

    def _calculate_defensive_actions(
        self, player: Player, minutes_factor: float  # TODO: добавить игрока
    ) -> float:
        """Рассчитать оборонительные действия"""
        # Заглушка - в реальности нужно больше данных
        base_value = 2.0  # tackles + interceptions per 90
        return base_value * minutes_factor if minutes_factor else 0

    def _estimate_progressive_actions(self, player: Player) -> float:
        """Оценить прогрессивные действия"""
        # Заглушка - зависит от позиции
        position_progressive = {
            Position.CM: 8.0,
            Position.CDM: 6.0,
            Position.CAM: 5.0,
            Position.CB: 5.0,
            Position.LB: 6.0,
            Position.RB: 6.0,
            Position.LW: 4.0,
            Position.RW: 4.0,
            Position.ST: 2.0,
            Position.GK: 1.0,
        }
        return (
            position_progressive.get(player.position, 4.0)
            * player.league_strength_coefficient
        )

    def _estimate_dribbling(self, player: Player) -> float:
        """Оценить дриблинг"""
        position_dribbling = {
            Position.LW: 4.0,
            Position.RW: 4.0,
            Position.CAM: 3.0,
            Position.CM: 2.0,
            Position.ST: 2.5,
            Position.LB: 2.0,
            Position.RB: 1.5,
            Position.CDM: 1.5,
            Position.CB: 0.5,
            Position.GK: 0.0,
        }
        return (
            position_dribbling.get(player.position, 1.5)
            * player.league_strength_coefficient
        )

    def _calculate_aerial_ability(self, player: Player) -> float:
        """Рассчитать способность в верховой борьбе"""
        # Зависит от роста и позиции
        height_factor = player.height_cm / 180.0

        position_aerial = {
            Position.CB: 1.2,
            Position.ST: 1.0,
            Position.CDM: 0.9,
            Position.CM: 0.7,
            Position.LB: 0.5,
            Position.RB: 0.5,
            Position.GK: 0.8,
            Position.LW: 0.4,
            Position.RW: 0.4,
            Position.CAM: 0.5,
        }

        return height_factor * position_aerial.get(player.position, 0.6)

    def _create_similar_player_dto(
        self,
        candidate: Player,
        similarity_score: float,
        target_player: Player,  # TODO: добавить игрока
    ) -> SimilarPlayerDTO:
        """Создать DTO похожего игрока"""
        # Ключевые статы для отображения
        minutes_factor = (
            90.0 / candidate.minutes_played if candidate.minutes_played > 0 else 0
        )

        key_stats = {
            "appearances": candidate.appearances,
            "goals": candidate.goals,
            "assists": candidate.assists,
            "goals_per_90": (
                round(candidate.goals * minutes_factor, 2) if minutes_factor else 0
            ),
            "assists_per_90": (
                round(candidate.assists * minutes_factor, 2) if minutes_factor else 0
            ),
            "xg_per_90": round(candidate.xg_per_90, 3),
            "xa_per_90": round(candidate.xa_per_90, 3),
            "age": candidate.age,
        }

        # Названия клуба и лиги (заглушки)
        club_name = (
            f"Club {candidate.current_club_id}"
            if candidate.current_club_id
            else "Free Agent"
        )
        league_name = (
            f"League {candidate.current_league_id}"
            if candidate.current_league_id
            else "Unknown"
        )

        return SimilarPlayerDTO(
            player_id=candidate.id,
            player_name=candidate.name,
            position=candidate.position.value,
            club_name=club_name,
            league_name=league_name,
            age=candidate.age,
            nationality=candidate.nationality,
            similarity_score=round(similarity_score, 3),
            market_value=candidate.market_value,
            key_stats=key_stats,
        )
