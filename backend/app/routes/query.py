"""
backend/app/routes/query.py
─────────────────────────────
POST /query
  Given a session_id and question, runs the RAG pipeline and returns an answer.
"""
import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_pipeline import run_rag
from app.services.vector_store import session_exists

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["Query"])


@router.post(
    "",
    response_model=QueryResponse,
    summary="Ask a question about an uploaded document",
)
async def query_document(body: QueryRequest):
    """
    Ask a natural language question about a previously uploaded document.

    - `session_id`: returned from POST /upload
    - `question`: your question in plain English

    Returns the generated answer and the source chunks used to produce it.
    """
    # ── Guard: session must exist ─────────────────────────────────────────────
    if not session_exists(body.session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{body.session_id}' not found. Please upload a document first.",
        )

    # ── Run RAG ───────────────────────────────────────────────────────────────
    try:
        answer, sources = run_rag(body.session_id, body.question)
    except ValueError as exc:
        # Config errors (missing API key, etc.)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.exception("RAG pipeline error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {exc}",
        )

    return QueryResponse(
        question=body.question,
        answer=answer,
        sources=sources,
    )
