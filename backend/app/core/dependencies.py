import redis.asyncio as aioredis
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGEngine, PGVectorStore
from langchain_postgres.v2.indexes import HNSWIndex

from app.core.config import settings
from app.core.model_factory import get_embedding_model

_redis_client: aioredis.Redis | None = None
_pg_engine: PGEngine | None = None
_vector_store: PGVectorStore | None = None

TABLE_NAME = "company_docs"


def get_embeddings() -> Embeddings:
    return get_embedding_model(settings.embedding_model)


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def get_pg_engine() -> PGEngine:
    global _pg_engine
    if _pg_engine is None:
        _pg_engine = PGEngine.from_connection_string(url=settings.database_url)
    return _pg_engine


async def init_vector_store_table() -> None:
    engine = await get_pg_engine()
    await engine.ainit_vectorstore_table(
        table_name=TABLE_NAME,
        vector_size=1536,
        overwrite_existing=False,
    )
    store = await get_vector_store()
    index = HNSWIndex(name="company_docs_hnsw_idx")
    await store.aapply_vector_index(index)


async def get_vector_store() -> PGVectorStore:
    global _vector_store
    if _vector_store is None:
        engine = await get_pg_engine()
        _vector_store = await PGVectorStore.create(
            engine=engine,
            table_name=TABLE_NAME,
            embedding_service=get_embeddings(),
        )
    return _vector_store


async def close_redis():
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def close_pg_engine():
    global _pg_engine, _vector_store
    _vector_store = None
    if _pg_engine is not None:
        await _pg_engine.close()
        _pg_engine = None
