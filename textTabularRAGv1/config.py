from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Server
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # Data
    DATA_DIR: str = "D:/financial_rag/Data/Craftsman Automations"
    CHROMA_PERSIST_DIR: str = "./chroma_store"

    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_DEVICE: str = "cuda"

    # Chunking
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma:7b"

    # RAG
    TOP_K_CHUNKS: int = 6

    # OpenAI
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()