from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://rag:rag_dev@localhost:5432/rag"
    database_url_sync: str = "postgresql://rag:rag_dev@localhost:5432/rag"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_docs"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "rag-documents"
    minio_secure: bool = False

    # LLM
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-6"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"

    # Embedding
    embedding_provider: str = "bge-m3"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024

    # Reranker
    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    # Chunking
    child_chunk_size: int = 400
    parent_chunk_size: int = 2500
    chunk_overlap: int = 50

    # Retrieval
    retrieval_top_k: int = 30
    rerank_top_n: int = 5

    # Limits
    max_upload_size_mb: int = 100
    max_pdf_pages: int = 2000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
