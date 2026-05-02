"""Сервис для построения радар-чартов игроков"""

import logging
from uuid import UUID

import numpy as np

from src.backend.nsi_service.application.dto import PlayerRadarDTO, RadarMetricDTO
from src.backend.nsi_service.domain.entities.player import Player
from src.backend.nsi_service.domain.interfaces.repositories import (
    ILeagueRepository,
    IPlayerRepository,
)
from src.backend.nsi_service.domain.value_objects.position import Position

logger = logging.getLogger(__name__)


# Метрики для радар-чартов по позициям
RADAR_METRICS_BY_POSITION = {
    Position.ST: [
        "goals_per_90",
        "xg_per_90",
        "shots_per_90",
        "touches_in_box_per_90",
        "aerial_duels_won_pct",
    ],
    Position.LW: [
        "goals_per_90",
        "assists_per_90",
        "dribbles_completed_per_90",
        "progressive_carries_per_90",
        "shots_per_90",
    ],
    Position.RW: [
        "goals_per_90",
        "assists_per_90",
        "dribbles_completed_per_90",
        "progressive_carries_per_90",
        "shots_per_90",
    ],
    Position.CAM: [
        "assists_per_90",
        "xa_per_90",
        "key_passes_per_90",
        "progressive_passes_per_90",
        "dribbles_completed_per_90",
    ],
    Position.CM: [
        "passes_completed_pct",
        "progressive_passes_per_90",
        "tackles_per_90",
        "interceptions_per_90",
        "progressive_carries_per_90",
    ],
    Position.CDM: [
        "tackles_per_90",
        "interceptions_per_90",
        "passes_completed_pct",
        "progressive_passes_per_90",
        "aerial_duels_won_pct",
    ],
    Position.LB: [
        "tackles_per_90",
        "interceptions_per_90",
        "progressive_carries_per_90",
        "crosses_per_90",
        "passes_completed_pct",
    ],
    Position.RB: [
        "tackles_per_90",
        "interceptions_per_90",
        "progressive_carries_per_90",
        "crosses_per_90",
        "passes_completed_pct",
    ],
    Position.CB: [
        "tackles_per_90",
        "interceptions_per_90",
        "aerial_duels_won_pct",
        "passes_completed_pct",
        "progressive_passes_per_90",
    ],
    Position.GK: [
        "save_pct",
        "clean_sheet_pct",
        "goals_prevented",
        "passes_completed_pct",
        "avg_pass_length",
    ],
}

# Названия метрик для отображения
METRIC_DISPLAY_NAMES = {
    "goals_per_90": "Голы (90)",
    "assists_per_90": "Ассисты (90)",
    "xg_per_90": "xG (90)",
    "xa_per_90": "xA (90)",
    "shots_per_90": "Удары (90)",
    "key_passes_per_90": "Ключевые передачи (90)",
    "dribbles_completed_per_90": "Дриблинг (90)",
    "tackles_per_90": "Отборы (90)",
    "interceptions_per_90": "Перехваты (90)",
    "passes_completed_pct": "Точность передач %",
    "progressive_passes_per_90": "Прогрессивные передачи (90)",
    "progressive_carries_per_90": "Прогрессивные рывки (90)",
    "aerial_duels_won_pct": "Верховые дуэли %",
    "touches_in_box_per_90": "Касания в штрафной (90)",
    "crosses_per_90": "Навесы (90)",
    "save_pct": "Процент сейвов",
    "clean_sheet_pct": "Сухие матчи %",
    "goals_prevented": "Предотвращённые голы",
    "avg_pass_length": "Средняя длина передачи",
}


class RadarChartService:
    """Сервис для построения радар-чартов"""

    def __init__(
        self,
        player_repository: IPlayerRepository,
        league_repository: ILeagueRepository,
    ):
        self.player_repo = player_repository
        self.league_repo = league_repository

    async def build_player_radar(
        self,
        player: Player,
        include_league_average: bool = True,
    ) -> PlayerRadarDTO:
        """
        Построить радар-чарт для игрока.

        Args:
            player: Доменная сущность игрока
            include_league_average: Включить средние значения лиги

        Returns:
            PlayerRadarDTO с данными для радар-чарта
        """
        # Получение метрик для позиции игрока
        position = player.position
        metrics_config = RADAR_METRICS_BY_POSITION.get(
            position, RADAR_METRICS_BY_POSITION[Position.CM]
        )

        # Получение данных игрока
        player_metrics = self._extract_player_metrics(player, metrics_config)

        # Получение средних значений по лиге
        league_avg_metrics: dict[str, float] = {}
        if include_league_average and player.current_league_id:
            league_avg_metrics = await self._calculate_league_averages(
                player.current_league_id,
                position,
                metrics_config,
            )

        # Формирование DTO
        radar_metrics = [
            RadarMetricDTO(
                name=METRIC_DISPLAY_NAMES.get(metric, metric),
                value=player_metrics.get(metric, 0.0),
                percentile=self._calculate_percentile(
                    player_metrics.get(metric, 0.0),
                    metric,
                    position,
                ),
                league_average=(
                    league_avg_metrics.get(metric, 0.0) if league_avg_metrics else 0.0
                ),
                position_average=0.0,  # TODO: Calculate position average
            )
            for metric in metrics_config
        ]

        league_avg_dto = (
            [
                RadarMetricDTO(
                    name=METRIC_DISPLAY_NAMES.get(metric, metric),
                    value=(
                        league_avg_metrics.get(metric, 0.0)
                        if league_avg_metrics
                        else 0.0
                    ),
                    percentile=50.0,
                    league_average=(
                        league_avg_metrics.get(metric, 0.0)
                        if league_avg_metrics
                        else 0.0
                    ),
                    position_average=0.0,
                )
                for metric in metrics_config
            ]
            if include_league_average
            else []
        )

        # Получение названия лиги
        league_name = "Unknown"
        if player.current_league_id:
            league = await self.league_repo.get_by_id(player.current_league_id)
            if league:
                league_name = league.name

        return PlayerRadarDTO(
            player_id=player.id,
            player_name=player.name,
            position=position.value,
            metrics=radar_metrics,
            league_name=league_name,
            league_average_metrics=league_avg_dto,
        )

    def _extract_player_metrics(
        self, player: Player, metrics_config: list[str]
    ) -> dict[str, float]:
        """Извлечь метрики из сущности игрока"""
        metrics = {}

        # Базовые метрики из сущности
        if player.minutes_played > 0:
            minutes_factor = 90.0 / player.minutes_played
            metrics["goals_per_90"] = player.goals * minutes_factor
            metrics["assists_per_90"] = player.assists * minutes_factor
            metrics["xg_per_90"] = player.xg_per_90
            metrics["xa_per_90"] = player.xa_per_90
        else:
            metrics["goals_per_90"] = 0.0
            metrics["assists_per_90"] = 0.0
            metrics["xg_per_90"] = 0.0
            metrics["xa_per_90"] = 0.0

        # Заглушки для метрик, которые требуют дополнительных данных
        placeholder_metrics = {
            "shots_per_90": 2.5,
            "key_passes_per_90": 1.5,
            "dribbles_completed_per_90": 1.0,
            "tackles_per_90": 2.0,
            "interceptions_per_90": 1.5,
            "passes_completed_pct": 85.0,
            "progressive_passes_per_90": 5.0,
            "progressive_carries_per_90": 3.0,
            "aerial_duels_won_pct": 50.0,
            "touches_in_box_per_90": 5.0,
            "crosses_per_90": 2.0,
            "save_pct": 70.0,
            "clean_sheet_pct": 35.0,
            "goals_prevented": 0.0,
            "avg_pass_length": 15.0,
        }

        for metric in metrics_config:
            if metric not in metrics:
                # Применяем коэффициент силы лиги
                base_value = placeholder_metrics.get(metric, 0.0)
                metrics[metric] = base_value * player.league_strength_coefficient

        return metrics

    async def _calculate_league_averages(
        self,
        league_id: UUID,
        position: Position,
        metrics_config: list[str],
    ) -> dict[str, float]:
        """Рассчитать средние значения по лиге для позиции"""
        # Получение всех игроков лиги
        players = await self.player_repo.get_by_league(league_id, limit=500)

        # Фильтрация по позиции
        position_players = [
            p for p in players if p.position == position and p.minutes_played > 0
        ]

        if not position_players:
            return dict.fromkeys(metrics_config, 0.0)

        # Расчет средних значений
        averages = {}
        for metric in metrics_config:
            values = self._get_values_by_metric(metric, position_players)
            if values:
                averages[metric] = float(np.mean(values))
            else:
                averages[metric] = 0.0

        return averages

    def _calculate_percentile(
        self,
        value: float,
        metric: str,
        position: Position,  # noqa
    ) -> float:
        """
        Рассчитать процентиль значения метрики.

        В реальной реализации здесь должно быть сравнение с базой данных
        всех игроков. Для прототипа используем упрощенную логику.
        """
        # Упрощенная логика для прототипа
        # В продакшене нужно сравнивать с распределением по лиге/позиции

        # Примерные пороги для топ-метрик
        thresholds: dict[str, list[float]] = {
            "goals_per_90": [0.3, 0.5, 0.7, 1.0],
            "assists_per_90": [0.2, 0.35, 0.5, 0.7],
            "xg_per_90": [0.3, 0.5, 0.7, 0.9],
            "xa_per_90": [0.2, 0.3, 0.45, 0.6],
            "passes_completed_pct": [75, 82, 88, 92],
            "tackles_per_90": [1.5, 2.5, 3.5, 5.0],
            "dribbles_completed_per_90": [0.5, 1.5, 2.5, 4.0],
        }

        metric_thresholds = thresholds.get(metric, [0.25, 0.5, 0.75, 1.0])

        if value >= metric_thresholds[-1]:
            return 95.0
        elif value >= metric_thresholds[-2]:
            return (
                75.0
                + (value - metric_thresholds[-2])
                / (metric_thresholds[-1] - metric_thresholds[-2])
                * 20
            )
        elif value >= metric_thresholds[-3]:
            return (
                50.0
                + (value - metric_thresholds[-3])
                / (metric_thresholds[-2] - metric_thresholds[-3])
                * 25
            )
        elif value >= metric_thresholds[-4]:
            return (
                25.0
                + (value - metric_thresholds[-4])
                / (metric_thresholds[-3] - metric_thresholds[-4])
                * 25
            )
        else:
            return max(0, value / metric_thresholds[0] * 25)

    @staticmethod
    def _get_values_by_metric(
        metric: str, position_players: list[Player]
    ) -> list[float]:
        values = []
        for player in position_players:
            if player.minutes_played > 0:
                minutes_factor = 90.0 / player.minutes_played
                if metric == "goals_per_90":
                    values.append(player.goals * minutes_factor)
                elif metric == "assists_per_90":
                    values.append(player.assists * minutes_factor)
                elif metric == "xg_per_90":
                    values.append(player.xg_per_90)
                elif metric == "xa_per_90":
                    values.append(player.xa_per_90)
        return values
