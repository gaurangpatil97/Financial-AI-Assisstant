from pathlib import Path
from logger import logger
from app.core.pdf_processor import extract_pdf
from app.core.excel_processor import extract_excel

SUPPORTED_EXTENSIONS = {
    ".pdf": extract_pdf,
    ".xlsx": extract_excel,
    ".xls": extract_excel,
    ".csv": extract_excel,
}

def route_document(file_path: str) -> list[dict]:
    """
    Detects file type and routes to correct processor.
    Returns list of dicts with content and metadata.
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        logger.error(f"Unsupported file type: {ext}")
        raise ValueError(f"Unsupported file type: {ext}")

    logger.info(f"Routing {file_path.name} → {ext} processor")
    processor = SUPPORTED_EXTENSIONS[ext]
    return processor(str(file_path))