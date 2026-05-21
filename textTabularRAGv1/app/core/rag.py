import ollama
from logger import logger
from config import get_settings
from app.core.embedder import generate_embeddings
from app.db.vector_store import query_collection, query_collection_by_type
from app.models.schemas import Citation, QueryResponse

settings = get_settings()

def build_prompt(question: str, chunks: list[dict]) -> str:
    context = ""
    for i, chunk in enumerate(chunks, start=1):
        context += f"\n[{i}] From {chunk['metadata']['filename']} (Page {chunk['metadata']['page']}):\n"
        context += chunk["content"] + "\n"

    prompt = f"""You are a financial expert assistant helping a Chartered Accountant (CA).
Use ONLY the context provided below to answer the question.
The context includes both text extracts and IMAGE CONTENT sections — treat IMAGE CONTENT sections as valid financial data.
Always cite the source document and page number for every claim you make.
If the answer is not in the context, say "I could not find this information in the provided documents."

Context:
{context}

Question: {question}

Answer:"""
    return prompt

def query_rag(question: str, collection_names: list[str], year: str = None) -> QueryResponse:
    logger.info(f"Processing query: {question}")

    # Embed the question
    query_chunks = [{"content": question, "metadata": {}, "embedding": None}]
    query_embedding = generate_embeddings(query_chunks)[0]["embedding"]

    # Retrieve text chunks
    all_chunks = []
    for collection_name in collection_names:
        chunks = query_collection(query_embedding, collection_name, year=year)
        all_chunks.extend(chunks)

    # Image chunks disabled — text-only retrieval for stable 70% baseline
    # for collection_name in collection_names:
    #     image_chunks = query_collection_by_type(
    #         query_embedding, collection_name,
    #         chunk_type="image", year=year, top_k=3
    #     )
    #     print(f"DEBUG IMAGE CHUNKS: {len(image_chunks)}")
    #     all_chunks.extend(image_chunks)

    all_chunks = sorted(all_chunks, key=lambda x: x["score"], reverse=True)
    top_chunks = all_chunks[:settings.TOP_K_CHUNKS]

    # Build prompt
    prompt = build_prompt(question, top_chunks)

    # Call Ollama
    logger.info(f"Calling Ollama model: {settings.OLLAMA_MODEL}")
    response = ollama.chat(
        model=settings.OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response["message"]["content"]

    # Build citations
    citations = []
    seen = set()
    for chunk in top_chunks:
        key = (chunk["metadata"]["filename"], chunk["metadata"]["page"])
        if key not in seen:
            seen.add(key)
            citations.append(Citation(
                filename=chunk["metadata"]["filename"],
                page=chunk["metadata"]["page"],
                collection=chunk["metadata"].get("collection", "unknown")
            ))

    logger.success(f"Query answered with {len(citations)} citations")
    return QueryResponse(
        answer=answer,
        citations=citations,
        collections_searched=collection_names
    )