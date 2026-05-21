from pathlib import Path
from logger import logger
from app.core.pdf_processor import extract_images_from_pdf
from app.core.chunker import chunk_documents
from app.core.embedder import generate_embeddings
from app.db.vector_store import store_chunks

# Only annual reports — not MGT7 or Annual Returns
ANNUAL_REPORTS = [
    ("D:/financial_rag/Data/Craftsman Automations/2022/7.-Annual-Report-2021-22.pdf", "2022"),
    ("D:/financial_rag/Data/Craftsman Automations/2023/Annual-Report_2023.pdf", "2023"),
    ("D:/financial_rag/Data/Craftsman Automations/2024/Annual-Report-2023-24.pdf", "2024"),
    ("D:/financial_rag/Data/Craftsman Automations/2025/Annual-Report-2025.pdf", "2025"),
]

def ingest_images(file_path: str, year: str):
    """Extract image descriptions and store in ChromaDB."""
    logger.info(f"Starting image ingestion: {file_path}")

    # Step 1 — Extract image descriptions via LLaVA
    pages_data = extract_images_from_pdf(file_path)

    if not pages_data:
        logger.warning(f"No image pages found in {file_path}")
        return

    # Step 2 — Add year to metadata
    for page in pages_data:
        page["metadata"]["year"] = year

    # Step 3 — Chunk
    chunks = chunk_documents(pages_data)

    # Step 4 — Embed
    chunks = generate_embeddings(chunks)

    # Step 5 — Store in same collection as text
    store_chunks(chunks, "ca_company_filings")

    logger.success(f"Done: {Path(file_path).name} — {len(chunks)} image chunks stored")

if __name__ == "__main__":
    # Start with just FY22 to test
    # Once confirmed working — uncomment the rest
    
    file_path, year = ANNUAL_REPORTS[0]
    ingest_images(file_path, year)
    
    # Uncomment below after confirming FY22 works:
    # for file_path, year in ANNUAL_REPORTS[1:]:
    #     ingest_images(file_path, year)
    #     logger.info(f"Completed {file_path}")