"""
backend/app/models/schemas.py
─────────────────────────────
Pydantic request/response models shared across routes.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ── Upload ────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    """Returned after a successful document upload + embedding."""
    session_id: str = Field(..., description="Unique identifier for this document session")
    filename: str = Field(..., description="Original filename")
    chunk_count: int = Field(..., description="Number of text chunks embedded")
    message: str = "Document processed and indexed successfully."


# ── Query ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Payload for asking a question against an indexed document."""
    session_id: str = Field(..., description="Session ID returned from /upload")
    question: str = Field(..., min_length=3, description="Natural language question")


class SourceChunk(BaseModel):
    """A single retrieved source chunk with metadata."""
    content: str = Field(..., description="Text content of the chunk")
    source: str = Field(..., description="Filename of the source document")
    page: Optional[int] = Field(None, description="Page number (PDFs only)")
    chunk_index: Optional[int] = Field(None, description="Chunk index within the document")


class QueryResponse(BaseModel):
    """Full answer with supporting source chunks."""
    question: str
    answer: str
    sources: List[SourceChunk] = Field(default_factory=list)


# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
