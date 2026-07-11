"""
backend/app/routes/upload.py
──────────────────────────────
POST /upload
  Accepts a PDF or text file, processes and embeds it, returns a session_id.
"""
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import settings
from app.models.schemas import UploadResponse
from app.services.document_processor import process_file
from app.services.vector_store import build_and_persist

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE_MB = 20


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and index a document",
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or text file.

    - Saves the file to the upload directory
    - Parses and chunks the document
    - Embeds chunks with HuggingFace sentence-transformers
    - Persists a FAISS vector index keyed by a unique session_id
    - Returns the session_id to use for subsequent /query calls
    """
    # ── Validate extension ────────────────────────────────────────────────────
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # ── Read & size-check ─────────────────────────────────────────────────────
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Maximum allowed: {MAX_FILE_SIZE_MB} MB",
        )

    # ── Persist file ──────────────────────────────────────────────────────────
    session_id = str(uuid.uuid4())
    safe_name = f"{session_id}_{file.filename}"
    dest_path = settings.upload_path / safe_name
    dest_path.write_bytes(content)
    logger.info("Saved upload: %s (%0.2f MB)", dest_path, size_mb)

    # ── Process ───────────────────────────────────────────────────────────────
    try:
        chunks = process_file(dest_path)
    except ValueError as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc))

    # ── Embed & store ─────────────────────────────────────────────────────────
    try:
        vector_count = build_and_persist(session_id, chunks)
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        logger.exception("Failed to build vector store: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {exc}",
        )

    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        chunk_count=vector_count,
    )
