import redis.asyncio as aioredis
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from app.core.config import settings

_redis_client: aioredis.Redis | None = None
_vector_store: PGVector | None = None


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def get_vector_store() -> PGVector:
    global _vector_store
    if _vector_store is None:
        connection_string = settings.database_url.replace("+asyncpg", "+psycopg")
        _vector_store = PGVector(
            embeddings=get_embeddings(),
            collection_name="company_docs",
            connection=connection_string,
            use_jsonb=True,
        )
    return _vector_store


async def close_redis():
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
