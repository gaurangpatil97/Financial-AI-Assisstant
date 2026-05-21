import chromadb
from chromadb.config import Settings as ChromaSettings
from logger import logger
from config import get_settings

settings = get_settings()

client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIR,
    settings=ChromaSettings(anonymized_telemetry=False)
)

def get_or_create_collection(collection_name: str):
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    logger.info(f"Collection ready: {collection_name}")
    return collection

def store_chunks(chunks: list[dict], collection_name: str):
    collection = get_or_create_collection(collection_name)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_type = chunk["metadata"].get("chunk_type", "text")
        chunk_id = f"{chunk['metadata']['filename']}_p{chunk['metadata']['page']}_c{chunk['metadata']['chunk_index']}_{chunk_type}"

        ids.append(chunk_id)
        embeddings.append(chunk["embedding"])
        documents.append(chunk["content"])

        meta = chunk["metadata"].copy()
        meta["collection"] = collection_name
        metadatas.append(meta)

    batch_size = 5000
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
        logger.info(f"Stored batch {i//batch_size + 1}")

    logger.success(f"Stored {len(chunks)} chunks in '{collection_name}'")

def query_collection(
    query_embedding: list[float],
    collection_name: str,
    top_k: int = None,
    year: str = None
) -> list[dict]:
    top_k = top_k or settings.TOP_K_CHUNKS
    collection = get_or_create_collection(collection_name)

    where = {"year": year} if year else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "content": doc,
            "metadata": meta,
            "score": 1 - dist
        })

    logger.info(f"Retrieved {len(chunks)} chunks from '{collection_name}'")
    return chunks

def query_collection_by_type(
    query_embedding: list[float],
    collection_name: str,
    chunk_type: str,
    top_k: int = 3,
    year: str = None
) -> list[dict]:
    collection = get_or_create_collection(collection_name)

    where = {"chunk_type": chunk_type}
    if year:
        where = {"$and": [{"chunk_type": chunk_type}, {"year": year}]}

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            chunks.append({
                "content": doc,
                "metadata": meta,
                "score": 1 - dist
            })

        logger.info(f"Retrieved {len(chunks)} image chunks from '{collection_name}'")
        return chunks

    except Exception as e:
        logger.error(f"Image chunk query failed: {e}")
        return []