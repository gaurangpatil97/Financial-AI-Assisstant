from pathlib import Path
from logger import logger
from app.core.doc_router import route_document
from app.core.excel_processor import extract_excel
from app.core.chunker import chunk_documents
from app.core.embedder import generate_embeddings
from app.db.vector_store import store_chunks
from config import get_settings

settings = get_settings()

# Map folder year to collections
# Since annual reports cover everything we put them in company filings
# and financial statements
COLLECTION_MAPPING = {
    "Annual-Report": "ca_company_filings",
    "Annual-Return": "ca_company_filings",
    "Financial": "ca_financial_statements",
    "GST": "ca_gst_documents",
    "Tax": "ca_tax_documents",
    "Audit": "ca_audit_reports",
}

def get_collection(filename: str) -> str:
    """Determines which collection a file belongs to based on filename."""
    for keyword, collection in COLLECTION_MAPPING.items():
        if keyword.lower() in filename.lower():
            return collection
    return "ca_miscellaneous"

def ingest_all():
    data_dir = Path(settings.DATA_DIR)
    
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return

    all_files = list(data_dir.rglob("*.pdf")) + \
                list(data_dir.rglob("*.xlsx")) + \
                list(data_dir.rglob("*.csv"))

    logger.info(f"Found {len(all_files)} files to ingest")

    for file_path in all_files:
        try:
            logger.info(f"Ingesting: {file_path.name}")

            # Extract year from parent folder name
            year = file_path.parent.name
            if not year.isdigit():
                year = "unknown"

            # Step 1 — Extract
            pages_data = route_document(str(file_path))

            # Add year to every page's metadata
            for page in pages_data:
                page["metadata"]["year"] = year

            # Step 2 — Chunk
            chunks = chunk_documents(pages_data)

            # Step 3 — Embed
            chunks = generate_embeddings(chunks)

            # Step 4 — Store
            collection = get_collection(file_path.name)
            store_chunks(chunks, collection)

            logger.success(f"Done: {file_path.name} → {collection} (Year: {year})")

        except Exception as e:
            logger.error(f"Failed to ingest {file_path.name}: {e}")
            continue

    logger.success("All files ingested successfully!")

def ingest_excel_only():
    if settings.EXPERIMENT != "exp1":
        logger.info(f"Skipping Excel-only ingest for experiment: {settings.EXPERIMENT}")
        return

    pages_data = extract_excel(settings.EXCEL_FILE_PATH)
    chunks = chunk_documents(pages_data)
    chunks = generate_embeddings(chunks)
    store_chunks(chunks, "ca_structured_financials")
    logger.success(f"Stored {len(chunks)} chunks in 'ca_structured_financials'")
    
if __name__ == "__main__":
    if get_settings().EXPERIMENT == "exp1":
        ingest_excel_only()
    else:
        ingest_all()