"""Сервис для сбора данных со статистических платформ"""

import json
import logging
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.nsi_service.core.utils import utc_now
from src.nsi_service.infrastructure.api_clients.factory import StatsClientFactory
from src.nsi_service.infrastructure.db.tables import raw_stats_table

logger = logging.getLogger(__name__)


class DataCollectionService:
    """Сервис для сбора данных со статистических платформ"""

    def __init__(
        self,
        session: AsyncSession,
        stats_factory: StatsClientFactory,
    ):
        self.session = session
        self.stats_factory = stats_factory

    async def collect_player_data(
        self,
        player_id: str,
        sources: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Собрать данные игрока из всех источников.

        Args:
            player_id: ID игрока во внешней системе
            sources: Список источников (по умолчанию все)

        Returns:
            Объединенные данные из всех источников
        """
        if sources is None:
            sources = ["fbref", "transfermarkt", "understat"]

        collected_data: dict[str, Any] = {
            "player_id": player_id,
            "collected_at": utc_now().isoformat(),
            "sources": {},
        }

        for source in sources:
            try:
                client = self.stats_factory.get_client(source)
                data = await client.get_player_stats(player_id)

                # Сохранение сырых данных
                await self._save_raw_data(
                    source=source,
                    entity_type="player",
                    entity_id=player_id,
                    data=data,
                )

                collected_data["sources"][source] = data

            except Exception as e:
                logger.error(f"Failed to collect data from {source}: {e}")
                collected_data["sources"][source] = {"error": str(e)}

        return collected_data

    async def collect_club_data(
        self,
        club_id: str,
        sources: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Собрать данные клуба из всех источников"""
        if sources is None:
            sources = ["fbref", "transfermarkt"]

        collected_data: dict[str, Any] = {
            "club_id": club_id,
            "collected_at": utc_now().isoformat(),
            "sources": {},
        }

        for source in sources:
            try:
                client = self.stats_factory.get_client(source)
                data = await client.get_club_stats(club_id)

                await self._save_raw_data(
                    source=source,
                    entity_type="club",
                    entity_id=club_id,
                    data=data,
                )

                collected_data["sources"][source] = data

            except Exception as e:
                logger.error(f"Failed to collect data from {source}: {e}")
                collected_data["sources"][source] = {"error": str(e)}

        return collected_data

    async def _save_raw_data(
        self,
        source: str,
        entity_type: str,
        entity_id: str,
        data: dict[str, Any],
    ) -> None:
        """Сохранить сырые данные в базу"""
        query = raw_stats_table.insert().values(
            source=source,
            entity_type=entity_type,
            entity_id=entity_id,
            data=json.dumps(data),
            fetched_at=utc_now(),
            processed=False,
        )
        await self.session.execute(query)
        await self.session.commit()

    async def get_unprocessed_data(
        self,
        source: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Получить необработанные данные"""
        query = select(raw_stats_table).where(raw_stats_table.c.processed.is_(False))

        if source:
            query = query.where(raw_stats_table.c.source == source)

        query = query.limit(limit)
        result = await self.session.execute(query)
        rows = result.fetchall()

        return [dict(row._mapping) for row in rows]

    async def mark_data_processed(self, raw_id: int) -> None:
        """Отметить данные как обработанные"""
        query = (
            raw_stats_table.update()
            .where(raw_stats_table.c.id == raw_id)
            .values(processed=True)
        )
        await self.session.execute(query)
        await self.session.commit()
