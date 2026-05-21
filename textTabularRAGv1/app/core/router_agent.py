import ollama
import json
from logger import logger
from config import get_settings

settings = get_settings()

COLLECTION_MAP = {
    "financial": "ca_financial_statements",
    "audit": "ca_audit_reports",
    "tax": "ca_tax_documents",
    "gst": "ca_gst_documents",
    "filings": "ca_company_filings",
    "misc": "ca_miscellaneous",
}

ROUTER_PROMPT = """You are a routing agent for a financial document RAG system.
Given a user question, decide which collections to search and which year to filter by.

Available collections:
- filings: Annual reports, financial statements, P&L, balance sheet, revenue, profit, borrowings, depreciation, directors report (USE THIS FOR MOST FINANCIAL QUESTIONS)
- financial: Standalone financial statement files
- audit: Auditor reports, audit observations
- tax: Income tax returns, tax assessments
- gst: GST returns, GSTR1, GSTR3B, GSTR9
- misc: News articles, other documents

IMPORTANT: For questions about revenue, profit, borrowings, assets, liabilities, depreciation, equity — use "filings".

Respond ONLY in this exact JSON format, nothing else:
{{
    "collections": ["filings"],
    "year": "2024"
}}

If no specific year mentioned, set year to null.
If multiple collections needed, include all of them.

Question: {question}"""


def route_query(question: str) -> dict:
    """
    Uses LLM to decide which collections and year to search.
    Returns dict with collections list and year.
    """
    logger.info(f"Routing query: {question}")

    response = ollama.chat(
        model=settings.OLLAMA_MODEL,
        messages=[{
            "role": "user",
            "content": ROUTER_PROMPT.format(question=question)
        }]
    )

    raw = response["message"]["content"].strip()

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        json_str = raw[start:end]
        result = json.loads(json_str)

        # Map collection keys to full names
        collections = [
            COLLECTION_MAP.get(c, "ca_company_filings")
            for c in result.get("collections", ["filings"])
        ]

        # Extract year correctly from formats like "2023-24" → "2024"
        year_raw = result.get("year")
        if year_raw:
            year_str = str(year_raw)
            if "-" in year_str:
                parts = year_str.split("-")
                year = parts[-1]  # take last part e.g. "24" from "2023-24"
                if len(year) == 2:
                    year = "20" + year  # "24" → "2024"
            else:
                year = year_str
        else:
            year = None

        logger.info(f"Router decision → Collections: {collections}, Year: {year}")
        return {"collections": collections, "year": year}

    except Exception as e:
        logger.error(f"Router parsing failed: {e} — defaulting to all collections")
        return {
            "collections": list(COLLECTION_MAP.values()),
            "year": None
        }