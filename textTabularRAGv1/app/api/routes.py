from fastapi import APIRouter, HTTPException
from logger import logger
from app.models.schemas import QueryRequest, QueryResponse
from app.core.rag import query_rag
from app.core.router_agent import route_query
from config import get_settings

settings = get_settings()
router = APIRouter()

COLLECTION_MAP = {
    "financial": "ca_financial_statements",
    "audit": "ca_audit_reports",
    "tax": "ca_tax_documents",
    "gst": "ca_gst_documents",
    "filings": "ca_company_filings",
    "misc": "ca_miscellaneous",
}

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        # If user manually specifies collection and year — use those
        if request.collection:
            if request.collection not in COLLECTION_MAP:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid collection. Choose from: {list(COLLECTION_MAP.keys())}"
                )
            collections = [COLLECTION_MAP[request.collection]]
            year = request.year
        else:
            # Auto route using router agent
            route = route_query(request.question)
            collections = route["collections"]
            year = request.year or route["year"]

        logger.info(f"Query: '{request.question}' → Collections: {collections}, Year: {year}")
        response = query_rag(request.question, collections, year=year)
        return response

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))