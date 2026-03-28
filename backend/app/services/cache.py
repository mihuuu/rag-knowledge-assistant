import hashlib
import json

import structlog
from redis.asyncio import Redis

from app.core.config import settings

logger = structlog.get_logger()


def _cache_key(question: str) -> str:
    return f"rag:cache:{hashlib.sha256(question.encode()).hexdigest()}"


async def get_cached_response(redis: Redis, question: str) -> dict | None:
    key = _cache_key(question)
    data = await redis.get(key)
    if data:
        logger.info("Cache hit", question=question[:50])
        return json.loads(data)
    return None


async def set_cached_response(redis: Redis, question: str, response: str, sources: list[dict]) -> None:
    key = _cache_key(question)
    data = json.dumps({"response": response, "sources": sources})
    await redis.setex(key, settings.cache_ttl, data)
    logger.info("Cached response", question=question[:50])
