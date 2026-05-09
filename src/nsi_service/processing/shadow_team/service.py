"""Сервис для формирования shadow-team"""

import logging
from typing import Optional

from src.nsi_service.application.dto import ShadowTeamCandidateDTO, ShadowTeamDTO
from src.nsi_service.domain.entities.player import Player
from src.nsi_service.domain.entities.team import Team
from src.nsi_service.domain.value_objects.position import Position

logger = logging.getLogger(__name__)


# Приоритеты позиций для усиления
POSITION_PRIORITY = {
    Position.GK: 1.0,
    Position.CB: 1.2,
    Position.LB: 1.1,
    Position.RB: 1.1,
    Position.CDM: 1.3,
    Position.CM: 1.2,
    Position.CAM: 1.4,
    Position.LW: 1.3,
    Position.RW: 1.3,
    Position.ST: 1.5,
}

# Минимальное улучшение для рекомендации
MIN_IMPROVEMENT_THRESHOLD = 0.15  # 15% улучшение


class ShadowTeamService:
    """Сервис для формирования shadow-team"""

    def build_shadow_team(
        self,
        user_team: Team,
        all_players: list[Player],
        budget: Optional[float] = None,
    ) -> ShadowTeamDTO:
        """
        Построить shadow-team для усиления состава.

        Shadow-team - это набор игроков, которые могут усилить
        каждую позицию в команде пользователя.

        Args:
            user_team: Команда пользователя
            all_players: Все доступные игроки для сравнения
            budget: Опциональный бюджет на трансферы

        Returns:
            ShadowTeamDTO с кандидатами на усиление
        """
        candidates_by_position: dict[str, list[ShadowTeamCandidateDTO]] = {}
        total_improvement = 0.0

        # Анализ текущей команды
        team_positions = user_team.squad

        for position_str, player_ids in team_positions.items():
            try:
                position = Position(position_str)
            except ValueError:
                continue

            # Получение текущих игроков на позиции
            current_players = [p for p in all_players if str(p.id) in player_ids]

            # Поиск кандидатов на усиление
            candidates = self._find_position_candidates(
                position=position,
                current_players=current_players,
                all_players=all_players,
                budget=budget,
            )

            if candidates:
                candidates_by_position[position_str] = candidates
                # Считаем среднее улучшение по позиции
                avg_improvement = sum(c.improvement_score for c in candidates) / len(
                    candidates
                )
                total_improvement += avg_improvement * POSITION_PRIORITY.get(
                    position, 1.0
                )

        return ShadowTeamDTO(
            team_id=user_team.id,
            team_name=user_team.name,
            candidates=candidates_by_position,
            total_improvement_score=round(total_improvement, 3),
        )

    def _find_position_candidates(
        self,
        position: Position,
        current_players: list[Player],
        all_players: list[Player],
        budget: Optional[float] = None,
    ) -> list[ShadowTeamCandidateDTO]:
        """
        Найти кандидатов на усиление позиции.

        Args:
            position: Позиция для усиления
            current_players: Текущие игроки на позиции
            all_players: Все доступные игроки
            budget: Бюджет на трансферы

        Returns:
            Список кандидатов с лучшим score
        """
        if not current_players:
            # Если нет текущих игроков, возвращаем топ доступных
            return self._get_top_available_players(
                position=position,
                all_players=all_players,
                budget=budget,
                limit=3,
            )

        # Расчет среднего уровня текущих игроков
        current_avg_rating = (
            self._calculate_player_rating(current_players[0]) if current_players else 0
        )

        # Поиск игроков лучше текущих
        candidates = []
        for player in all_players:
            # Пропускаем текущих игроков
            if any(p.id == player.id for p in current_players):
                continue

            # Та же позиция
            if player.position != position:
                continue

            # Проверка бюджета
            if budget and player.market_value:
                if float(player.market_value) > budget:
                    continue

            # Расчет рейтинга и улучшения
            player_rating = self._calculate_player_rating(player)
            improvement = (player_rating - current_avg_rating) / max(
                current_avg_rating, 1
            )

            # Только если есть значимое улучшение
            if improvement >= MIN_IMPROVEMENT_THRESHOLD:
                candidate = self._create_candidate_dto(
                    player=player,
                    improvement_score=round(improvement, 3),
                )
                candidates.append(candidate)

        # Сортировка по улучшению
        candidates.sort(key=lambda x: x.improvement_score, reverse=True)
        return candidates[:3]  # Топ-3 кандидата на позицию

    def _get_top_available_players(
        self,
        position: Position,
        all_players: list[Player],
        budget: Optional[float] = None,
        limit: int = 3,
    ) -> list[ShadowTeamCandidateDTO]:
        """Получить топ доступных игроков на позицию"""
        # Фильтрация по позиции
        position_players = [p for p in all_players if p.position == position]

        # Проверка бюджета
        if budget:
            position_players = [
                p
                for p in position_players
                if not p.market_value or float(p.market_value) <= budget
            ]

        # Сортировка по рейтингу
        position_players.sort(
            key=lambda p: self._calculate_player_rating(p),
            reverse=True,
        )

        # Создание DTO
        candidates = []
        for player in position_players[:limit]:
            candidate = self._create_candidate_dto(
                player=player,
                improvement_score=0.0,  # Нет текущего игрока для сравнения
            )
            candidates.append(candidate)

        return candidates

    def _calculate_player_rating(self, player: Player) -> float:
        """
        Рассчитать общий рейтинг игрока.

        Используется упрощенная формула на основе ключевых метрик.
        """
        minutes_factor = (
            90.0 / player.minutes_played if player.minutes_played > 0 else 0
        )

        # Базовые очки от статов
        rating = 0.0

        # Голы и ассисты (нормализованные)
        goals_90 = player.goals * minutes_factor if minutes_factor else 0
        assists_90 = player.assists * minutes_factor if minutes_factor else 0
        rating += goals_90 * 10 + assists_90 * 7

        # Продвинутые метрики
        rating += player.xg_per_90 * 8
        rating += player.xa_per_90 * 6

        # Бонус за силу лиги
        rating *= player.league_strength_coefficient

        # Бонус за возраст (пик формы 24-29)
        age_bonus = 1.0
        if 24 <= player.age <= 29:
            age_bonus = 1.1
        elif player.age < 24:
            age_bonus = 1.0 + (24 - player.age) * 0.02
        elif player.age > 29:
            age_bonus = 1.0 - (player.age - 29) * 0.03

        rating *= max(0.8, age_bonus)

        return rating

    def _create_candidate_dto(
        self,
        player: Player,
        improvement_score: float,
    ) -> ShadowTeamCandidateDTO:
        """Создать DTO кандидата"""
        # Ключевые статы
        minutes_factor = (
            90.0 / player.minutes_played if player.minutes_played > 0 else 0
        )

        key_stats = {
            "appearances": player.appearances,
            "goals": player.goals,
            "assists": player.assists,
            "goals_per_90": (
                round(player.goals * minutes_factor, 2) if minutes_factor else 0
            ),
            "assists_per_90": (
                round(player.assists * minutes_factor, 2) if minutes_factor else 0
            ),
            "xg_per_90": round(player.xg_per_90, 3),
            "xa_per_90": round(player.xa_per_90, 3),
            "age": player.age,
            "market_value": str(player.market_value) if player.market_value else None,
        }

        # Названия клуба и лиги (заглушки)
        club_name = (
            f"Club {player.current_club_id}" if player.current_club_id else "Free Agent"
        )
        league_name = (
            f"League {player.current_league_id}"
            if player.current_league_id
            else "Unknown"
        )

        return ShadowTeamCandidateDTO(
            player_id=player.id,
            player_name=player.name,
            position=player.position.value,
            club_name=club_name,
            league_name=league_name,
            age=player.age,
            nationality=player.nationality,
            market_value=player.market_value,
            improvement_score=improvement_score,
            key_stats=key_stats,
        )
