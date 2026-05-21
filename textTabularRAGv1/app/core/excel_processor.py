import pandas as pd
from pathlib import Path
from logger import logger

def extract_excel(file_path: str) -> list[dict]:
    """
    Extracts data from Excel/CSV files.
    Returns list of dicts with content and metadata.
    """
    file_path = Path(file_path)
    filename = file_path.name
    pages_data = []

    logger.info(f"Processing Excel/CSV: {filename}")

    # Handle CSV separately
    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
        content = df.to_markdown(index=False)
        pages_data.append({
            "content": content,
            "metadata": {
                "filename": filename,
                "page": 1,
                "source": str(file_path),
            }
        })

    # Handle Excel — one "page" per sheet
    else:
        xl = pd.ExcelFile(file_path)
        for sheet_num, sheet_name in enumerate(xl.sheet_names, start=1):
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            content = f"Sheet: {sheet_name}\n" + df.to_markdown(index=False)
            
            if content.strip():
                pages_data.append({
                    "content": content.strip(),
                    "metadata": {
                        "filename": filename,
                        "page": sheet_num,
                        "source": str(file_path),
                    }
                })

    logger.success(f"Extracted {len(pages_data)} sheets/pages from {filename}")
    return pages_data