from datetime import datetime, timezone


def utc_now() -> datetime:
    """Вернуть текущее UTC время для default в колонках"""
    return datetime.now(timezone.utc)


__all__ = [
    "utc_now",
]
