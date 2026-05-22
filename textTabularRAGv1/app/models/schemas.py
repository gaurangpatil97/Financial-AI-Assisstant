from pydantic import BaseModel
from typing import List, Optional

class Citation(BaseModel):
    filename: str
    page: int | str
    collection: str

class QueryRequest(BaseModel):
    question: str
    collection: Optional[str] = None
    year: Optional[str] = None  # e.g. "2024", "2023"

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    collections_searched: List[str]
    agent_used: str = "rag"  # "rag" or "calculation_agent"
    agent_trace: str = ""  # shows what the agent did step by step