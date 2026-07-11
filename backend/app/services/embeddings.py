"""
backend/app/services/embeddings.py
────────────────────────────────────
Singleton HuggingFace embedding model.
Uses `sentence-transformers/all-MiniLM-L6-v2` locally (no API key needed).
"""
import logging
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns a cached HuggingFaceEmbeddings instance.
    The model is downloaded once on first call and cached in memory.
    """
    logger.info("Loading embedding model: %s", settings.embedding_model_id)
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.embedding_model_id,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    logger.info("Embedding model loaded.")
    return embeddings
