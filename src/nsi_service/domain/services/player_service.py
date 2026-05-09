from datetime import date

from src.nsi_service.domain.entities import Player


class PlayerService:
    @staticmethod
    def update_stats(  # NOSONAR(S3776)
        player: Player,
        appearances: int | None = None,
        goals: int | None = None,
        assists: int | None = None,
        yellow_cards: int | None = None,
        red_cards: int | None = None,
        minutes_played: int | None = None,
        xg: float | None = None,
        xa: float | None = None,
    ) -> Player:
        if appearances is not None:
            player.appearances += appearances
        if goals is not None:
            player.goals += goals
        if assists is not None:
            player.assists += assists
        if yellow_cards is not None:
            player.yellow_cards += yellow_cards
        if red_cards is not None:
            player.red_cards += red_cards
        if minutes_played is not None:
            player.minutes_played += minutes_played
        if xg is not None:
            player.xg = round(player.xg + xg, 4)
        if xa is not None:
            player.xa = round(player.xa + xa, 4)
        player.updated_at = date.today()
        return player
