"""
backend/app/main.py
────────────────────
FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, query
from app.config import settings

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("─" * 60)
    logger.info("  PDF RAG Server starting up")
    logger.info("  LLM  : %s", settings.llm_model_id)
    logger.info("  Embed: %s", settings.embedding_model_id)
    logger.info("  Chunk: size=%d  overlap=%d", settings.chunk_size, settings.chunk_overlap)
    logger.info("─" * 60)
    yield
    logger.info("PDF RAG Server shut down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PDF RAG — Document QA API",
    description="Upload documents and ask questions via Retrieval-Augmented Generation.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS — allow the frontend (served on any port during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
async def health():
    """Simple health check."""
    return {"status": "ok", "version": "1.0.0"}
