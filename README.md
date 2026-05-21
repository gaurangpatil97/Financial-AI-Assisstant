markdown# Financial AI Assistant — textTabularRAGv1

A local, GPU-accelerated RAG (Retrieval-Augmented Generation) pipeline for Chartered Accountants (CAs) to query financial documents in natural language and receive answers with exact citations (filename + page number).

## What It Does

- Upload financial PDFs and Excel files
- Ask natural language questions across documents
- Get answers with exact source citations (filename + page number)
- Automatic query routing — detects which collection and year to search
- Supports multi-year financial analysis (FY22-FY25)

## Tech Stack

| Component | Tool |
|---|---|
| API | FastAPI |
| PDF Parsing | pdfplumber (two-column aware) |
| Excel/CSV | Pandas |
| Embeddings | SentenceTransformers — BAAI/bge-large-en-v1.5 |
| Vector DB | ChromaDB |
| LLM | Ollama + Llama3.1:8b |
| Query Router | Llama3.1:8b (auto collection + year detection) |

## Hardware Requirements

- GPU: NVIDIA GPU with CUDA support (tested on RTX 4060 8GB)
- CUDA: 12.x
- RAM: 16GB+ recommended
- Storage: 20GB+ free (models + embeddings)

## Prerequisites

- Python 3.10
- CUDA 12.x drivers installed
- Ollama installed from [ollama.com](https://ollama.com)
- Git

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/gaurangpatil97/Financial-AI-Assisstant.git
cd Financial-AI-Assisstant
2. Set up environment variables
Before installing anything, set these environment variables:
Windows (PowerShell as Admin):
powershellsetx OLLAMA_MODELS "D:\ollama_models"
setx HF_HOME "D:\hf_models"
setx TESSDATA_PREFIX "D:\ocr_setup\tessdata"
Restart your terminal after setting these.
3. Create virtual environment
powershellcd textTabularRAGv1
python -m venv venv
venv\Scripts\activate
4. Install PyTorch with CUDA
powershellpip install torch --index-url https://download.pytorch.org/whl/cu121
5. Install dependencies
powershellpip install -r requirements.txt
6. Pull Ollama models
powershellollama pull llama3.1:8b
7. Create .env file
Create textTabularRAGv1/.env with:
envAPP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
DATA_DIR=./data
CHROMA_PERSIST_DIR=./chroma_store
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
EMBEDDING_DEVICE=cuda
CHUNK_SIZE=800
CHUNK_OVERLAP=150
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
TOP_K_CHUNKS=13
OPENAI_API_KEY=your_key_here
8. Prepare your documents
Create a data folder with year-based subfolders:
data/
├── 2022/
│   ├── Annual-Report-2021-22.pdf
│   └── Annual-Return-2022.pdf
├── 2023/
│   └── Annual-Report-2023.pdf
├── 2024/
│   └── Annual-Report-2023-24.pdf
└── 2025/
    └── Annual-Report-2025.pdf
Update DATA_DIR in .env to point to your data folder.
9. Ingest documents
powershellpython ingest.py
This will:

Extract text from all PDFs and Excel files
Generate embeddings using BAAI/bge-large-en-v1.5 on GPU
Store in ChromaDB

This runs once. Takes ~30-60 minutes depending on document count.
10. Start the server
powershellpython main.py
Server starts at http://localhost:8000
Usage
Query the RAG
PowerShell:
powershellInvoke-RestMethod -Uri "http://localhost:8000/api/v1/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "What was the net profit in FY23?"}' | ConvertTo-Json
With year filter:
powershellInvoke-RestMethod -Uri "http://localhost:8000/api/v1/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "What was the revenue?", "year": "2024"}' | ConvertTo-Json
With collection filter:
powershellInvoke-RestMethod -Uri "http://localhost:8000/api/v1/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "What are the audit observations?", "collection": "audit"}' | ConvertTo-Json
Available Collections
KeyCollectionDocumentsfinancialca_financial_statementsBalance Sheet, P&L, Cash Flowauditca_audit_reportsAuditor Reportstaxca_tax_documentsITR, Tax Assessmentsgstca_gst_documentsGSTR-1, GSTR-3B, GSTR-9filingsca_company_filingsAnnual Reports, Directors Reportmiscca_miscellaneousNews, Other Documents
Sample Response
json{
  "answer": "The net profit after tax for FY2022-23 was ₹237.76 Crores...",
  "citations": [
    {
      "filename": "Annual-Report_2023.pdf",
      "page": 24,
      "collection": "ca_company_filings"
    }
  ],
  "collections_searched": ["ca_company_filings"]
}
Project Structure
textTabularRAGv1/
├── main.py                    # FastAPI entry point
├── ingest.py                  # Document ingestion script
├── ingest_images_only.py      # Image-only ingestion (v2)
├── config.py                  # Settings
├── logger.py                  # Logging
├── test_pipeline.py           # Full test suite (40 questions)
├── test_pipeline2.py          # Annual reports test (20 questions)
├── RESULTS_text_table_only.md # Benchmark results
├── app/
│   ├── api/
│   │   └── routes.py          # POST /query endpoint
│   ├── core/
│   │   ├── pdf_processor.py   # PDF extraction (two-column + OCR)
│   │   ├── excel_processor.py # Excel/CSV extraction
│   │   ├── doc_router.py      # File type router
│   │   ├── chunker.py         # Text splitting
│   │   ├── embedder.py        # Embedding generation
│   │   ├── rag.py             # RAG chain
│   │   └── router_agent.py    # LLM query router
│   ├── db/
│   │   └── vector_store.py    # ChromaDB operations
│   └── models/
│       └── schemas.py         # Pydantic models
Accuracy Benchmark
Tested on Craftsman Automation FY22-FY25 Annual Reports (20 questions):
MetricScoreAnswer Accuracy70% (14/20)Citation Accuracy30% (6/20)
Known Limitations

Infographic/image-based pages not extractable (Q5, Q15, Q18)
Data buried in Directors Report has low retrieval rank
Citation page numbers sometimes differ from expected

Roadmap
v2 — Image Pipeline

GPT-4o vision for infographic pages (target 85%+ accuracy)
OCR pipeline already built — needs better vision model
Image pipeline code in pdf_processor.py (currently disabled)

v3 — Multi-Agent + Frontend

React frontend
Multi-agent cross-collection queries
Second company dataset validation
Audio ingestion (Whisper)

CPU-Only Setup (No GPU)
Change in .env:
envEMBEDDING_DEVICE=cpu
Note: Ingestion will be 5-10x slower without GPU.
Troubleshooting
Ollama not found:
powershell# Make sure Ollama is running
ollama serve
CUDA not enabled:
powershellpip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cu121
ChromaDB batch size error:
Already handled in vector_store.py — batches of 5000.
Tesseract OCR error:
powershellsetx TESSDATA_PREFIX "D:\ocr_setup\tessdata"
Download eng.traineddata from https://github.com/tesseract-ocr/tessdata
License
MIT

