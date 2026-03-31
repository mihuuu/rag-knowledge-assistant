from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/ragagent"

    # Redis
    redis_url: str = "redis://redis:6379"

    # App
    data_dir: str = "/app/data"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # LangSmith
    langsmith_tracing: bool = True
    langsmith_api_key: str = ""
    langsmith_project: str = "rag-knowledge-assistant"

    # Cohere
    cohere_api_key: str = ""

    # RAG settings
    chunk_size: int = 512
    chunk_overlap: int = 102
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    retrieval_k: int = 3
    rerank_model: str = "rerank-v3.5"
    rerank_candidates: int = 15

    # Cache
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_distance_threshold: float = 0.1

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
