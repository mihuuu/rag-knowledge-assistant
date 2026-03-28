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

    # RAG settings
    chunk_size: int = 512
    chunk_overlap: int = 102
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    retrieval_k: int = 5

    # Cache
    cache_ttl: int = 3600  # 1 hour

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
