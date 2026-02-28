from src.domain.entities import Club, League, Player, Team
from src.infrastructure.db.metadata import mapper_registry
from src.infrastructure.db.tables import (
    clubs_table,
    leagues_table,
    players_table,
    teams_table,
)


def setup_mapping() -> None:
    """
    Настроить маппинг SQLAlchemy для Entity.
    Должна вызываться один раз при старте приложения.
    """
    mapper_registry.map_imperatively(League, leagues_table)
    mapper_registry.map_imperatively(Club, clubs_table)
    mapper_registry.map_imperatively(Player, players_table)
    mapper_registry.map_imperatively(Team, teams_table)


__all__ = ["setup_mapping"]
