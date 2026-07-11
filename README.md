# DocQuery — AI-Powered Document Q&A

> Upload PDF or text documents and ask natural language questions powered by RAG, LangChain, and HuggingFace open-source models.

---

## Architecture

```
Upload (PDF / TXT / MD)
    → PyMuPDF parsing (page-by-page)
    → RecursiveCharacterTextSplitter (LangChain)
    → HuggingFace Embeddings (all-MiniLM-L6-v2) — local
    → FAISS vector index (persisted per session)
    ↓
Question
    → MMR Retrieval (top-k diverse chunks)
    → Custom prompt template
    → HuggingFace Inference API LLM (flan-t5 / Mistral)
    → Answer + Source chunks
```

## Folder Structure

```
Pdf RAG/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app
│   │   ├── config.py                # Settings via .env
│   │   ├── models/schemas.py        # Pydantic schemas
│   │   ├── services/
│   │   │   ├── document_processor.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   └── rag_pipeline.py
│   │   └── routes/
│   │       ├── upload.py            # POST /api/upload
│   │       └── query.py             # POST /api/query
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── tests/
    ├── test_upload.py
    └── test_query.py
```

## Quick Start

### 1. Clone & set up Python environment

```bash
cd "Pdf RAG/backend"
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Open .env and add your HuggingFace API token:
# HF_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Get a free token at: https://huggingface.co/settings/tokens

### 3. Start the backend

```bash
# From backend/
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/api/docs

### 4. Open the frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
cd ../frontend
python -m http.server 3000
# → http://localhost:3000
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload & index a document |
| `POST` | `/api/query`  | Ask a question about a document |

### POST /api/upload

```json
// Request: multipart/form-data
{ "file": "<PDF or TXT file>" }

// Response 201
{
  "session_id": "uuid-v4",
  "filename": "report.pdf",
  "chunk_count": 42,
  "message": "Document processed and indexed successfully."
}
```

### POST /api/query

```json
// Request
{
  "session_id": "uuid-v4",
  "question": "What are the main findings of this report?"
}

// Response 200
{
  "question": "What are the main findings...",
  "answer": "The main findings include...",
  "sources": [
    { "content": "...", "source": "report.pdf", "page": 3, "chunk_index": 12 }
  ]
}
```

## Running Tests

```bash
cd "Pdf RAG"
pip install -r backend/requirements.txt
pytest tests/ -v
```

> **Note**: Tests requiring the LLM (RAG answer generation) are automatically skipped if `HF_API_KEY` is not set in the environment.

## LLM Options

Configure `LLM_MODEL_ID` in your `.env`:

| Model | Speed | Quality | Notes |
|-------|-------|---------|-------|
| `google/flan-t5-base` | ⚡ Fast | Good | Default, free tier |
| `google/flan-t5-large` | Medium | Better | Free tier |
| `mistralai/Mistral-7B-Instruct-v0.2` | Slow | Excellent | May require Pro tier |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_API_KEY` | — | HuggingFace token (required) |
| `LLM_MODEL_ID` | `google/flan-t5-base` | HF Inference API model |
| `EMBEDDING_MODEL_ID` | `all-MiniLM-L6-v2` | Local embedding model |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K` | `4` | Retrieved chunks per query |
