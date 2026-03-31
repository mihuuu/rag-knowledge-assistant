import json

import structlog
from langchain_core.outputs import Generation
from langchain_redis import RedisSemanticCache
from langsmith import traceable

from app.core.config import settings
from app.core.dependencies import get_embeddings

logger = structlog.get_logger()

_semantic_cache: RedisSemanticCache | None = None


def get_semantic_cache() -> RedisSemanticCache:
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = RedisSemanticCache(
            redis_url=settings.redis_url,
            embeddings=get_embeddings(),
            distance_threshold=settings.cache_distance_threshold,
            ttl=settings.cache_ttl,
        )
    return _semantic_cache


@traceable(name="cache_lookup", run_type="chain")
def get_cached_response(question: str) -> dict | None:
    cache = get_semantic_cache()
    result = cache.lookup(question, "rag-chain")
    if result:
        gen = result[0]
        sources = json.loads(gen.generation_info["sources"]) if gen.generation_info else []
        logger.info("Semantic cache hit", question=question[:50])
        return {"response": gen.text, "sources": sources}
    return None


@traceable(name="cache_store", run_type="chain")
def set_cached_response(question: str, response: str, sources: list[dict]) -> None:
    cache = get_semantic_cache()
    gen = Generation(text=response, generation_info={"sources": json.dumps(sources)})
    cache.update(question, "rag-chain", [gen])
    logger.info("Cached response", question=question[:50])
