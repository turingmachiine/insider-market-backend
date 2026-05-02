import logging

import redis


class RedisListLogHandler(logging.Handler):
    def __init__(self, url: str, key: str) -> None:
        super().__init__()
        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._key = key

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._client.rpush(self._key, self.format(record))
        except Exception:
            return
