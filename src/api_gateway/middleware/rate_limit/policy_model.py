from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitPolicy:
    name: str
    limit_per_minute: int
