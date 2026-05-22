from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    EXPERIMENT: str = "exp1"
    EXCEL_FILE_PATH: str = "D:/financial_rag/Data/Infosys/Infosys.xlsx"
    # Server
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # Data
    DATA_DIR: str = "D:/financial_rag/Data/Craftsman Automations"
    # ═══════════════════════════════════════════════════
    # CHROMADB INSTANCE REGISTRY
    # ═══════════════════════════════════════════════════
    # ./chroma_store/exp1_excel_only        → Craftsman Auto, Excel only, exp1 baseline (19/30)
    # ./chroma_store/craftsman_exp1_excel   → Craftsman Auto, Excel + CalcAgent, exp1 final (28/30)
    # ./chroma_store/infosys_exp1_excel     → Infosys, Excel only, exp1 generalization test
    # ═══════════════════════════════════════════════════
    # TO SWITCH: change CHROMA_PERSIST_DIR to the instance you want
    # TO SWITCH COMPANY: change EXCEL_FILE_PATH accordingly
    # ═══════════════════════════════════════════════════
    CHROMA_PERSIST_DIR: str = "./chroma_store/infosys_exp1_excel"

    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_DEVICE: str = "cuda"

    # Chunking
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

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