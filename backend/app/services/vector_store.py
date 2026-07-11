"""
backend/app/services/vector_store.py
─────────────────────────────────────
FAISS-based vector store manager.

Each upload session gets its own subdirectory under vector_store_dir,
named by session_id. This allows multiple documents to coexist and be
queried independently.
"""
import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.config import settings
from app.services.embeddings import get_embeddings

logger = logging.getLogger(__name__)


def _session_path(session_id: str) -> Path:
    """Returns the directory path for a session's FAISS index."""
    return settings.vector_store_path / session_id


def build_and_persist(session_id: str, chunks: List[Document]) -> int:
    """
    Embed `chunks` and save a FAISS index to disk for `session_id`.
    Returns the number of vectors stored.
    """
    embeddings = get_embeddings()
    store = FAISS.from_documents(chunks, embeddings)

    dest = _session_path(session_id)
    dest.mkdir(parents=True, exist_ok=True)
    store.save_local(str(dest))

    count = store.index.ntotal
    logger.info("Stored %d vectors for session '%s' at %s", count, session_id, dest)
    return count


def load_store(session_id: str) -> FAISS:
    """
    Load a persisted FAISS index from disk for `session_id`.
    Raises FileNotFoundError if the session does not exist.
    """
    dest = _session_path(session_id)
    if not dest.exists():
        raise FileNotFoundError(
            f"No vector store found for session '{session_id}'. "
            "Please upload a document first."
        )
    embeddings = get_embeddings()
    store = FAISS.load_local(
        str(dest),
        embeddings,
        allow_dangerous_deserialization=True,  # safe: local files only
    )
    logger.info("Loaded FAISS index for session '%s'", session_id)
    return store


def session_exists(session_id: str) -> bool:
    """Check whether a vector store exists for the given session."""
    return _session_path(session_id).exists()
