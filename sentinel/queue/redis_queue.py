import json
from typing import Any

import redis

from sentinel.config import Settings

settings = Settings()


class RedisQueue:
    def __init__(self, queue_name: str = "sentinel:ingest"):
        self.client = redis.from_url(settings.redis_url, decode_responses=True)
        self.queue_name = queue_name

    def enqueue(self, item: dict[str, Any]) -> None:
        self.client.lpush(self.queue_name, json.dumps(item))

    def dequeue(self, timeout: int = 5) -> dict[str, Any] | None:
        result = self.client.brpop(self.queue_name, timeout=timeout)
        if result:
            item: dict[str, Any] = json.loads(result[1])
            return item
        return None

    def flush(self) -> None:
        self.client.delete(self.queue_name)

    @property
    def size(self) -> int:
        return self.client.llen(self.queue_name)
