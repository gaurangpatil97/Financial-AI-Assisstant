import uvicorn
from fastapi import FastAPI
from app.api.routes import router
from logger import logger
from config import get_settings

settings = get_settings()

app = FastAPI(
    title="Financial Intelligence RAG",
    description="CA Document Intelligence System — Craftsman Automation",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}

if __name__ == "__main__":
    logger.info("Starting Financial RAG Server...")
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )