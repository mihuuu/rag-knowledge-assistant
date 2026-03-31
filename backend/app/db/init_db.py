from sqlalchemy import text

from app.db.session import engine
from app.models.database import Base


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_langchain_pg_embedding_hnsw
                ON langchain_pg_embedding
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
                """
            )
        )
