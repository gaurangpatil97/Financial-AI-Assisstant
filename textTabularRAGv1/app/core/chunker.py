from langchain_text_splitters import RecursiveCharacterTextSplitter
from logger import logger
from config import get_settings

settings = get_settings()

def chunk_documents(pages_data: list[dict]) -> list[dict]:
    """
    Takes pages data and splits into smaller chunks.
    Preserves metadata (filename, page number) on every chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = []
    for page in pages_data:
        splits = splitter.split_text(page["content"])
        
        for chunk_idx, split in enumerate(splits):
            chunks.append({
                "content": split,
                "metadata": {
                    **page["metadata"],
                    "chunk_index": chunk_idx,
                }
            })

    logger.info(f"Created {len(chunks)} chunks from {len(pages_data)} pages")
    return chunks