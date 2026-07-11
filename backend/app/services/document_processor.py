"""
backend/app/services/document_processor.py
───────────────────────────────────────────
Parses uploaded files (PDF or plain text) into LangChain Documents,
then splits them into chunks ready for embedding.
"""
import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger(__name__)

# ── PDF backend detection ─────────────────────────────────────────────────────
try:
    import fitz  # PyMuPDF — preferred: fast, page-level metadata
    _PYMUPDF = True
except ImportError:
    _PYMUPDF = False
    logger.warning("PyMuPDF (fitz) not available — falling back to pypdf")

try:
    from pypdf import PdfReader  # pure-Python fallback
    _PYPDF = True
except ImportError:
    _PYPDF = False


# ── Text Cleaning ─────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """
    Clean extracted document text.
    Replaces single newlines (line wraps) with spaces to preserve sentence flow,
    while keeping double newlines to define paragraph boundaries.
    """
    if not text:
        return ""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split by double newline to preserve paragraphs
    paragraphs = text.split("\n\n")
    cleaned_paragraphs = []
    for p in paragraphs:
        # Merge lines inside paragraph
        lines = [line.strip() for line in p.split("\n") if line.strip()]
        if lines:
            cleaned_paragraphs.append(" ".join(lines))
    return "\n\n".join(cleaned_paragraphs)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_pdf(file_path: Path) -> List[Document]:
    """Extract text page-by-page from a PDF, using PyMuPDF or pypdf as fallback."""
    if _PYMUPDF:
        docs: List[Document] = []
        with fitz.open(str(file_path)) as pdf:
            for page_num, page in enumerate(pdf, start=1):
                raw_text = page.get_text("text").strip()
                text = _clean_text(raw_text)
                if text:
                    docs.append(
                        Document(
                            page_content=text,
                            metadata={"source": file_path.name, "page": page_num},
                        )
                    )
        logger.info("PyMuPDF: parsed and cleaned %d pages from '%s'", len(docs), file_path.name)
        return docs

    elif _PYPDF:
        docs = []
        reader = PdfReader(str(file_path))
        for page_num, page in enumerate(reader.pages, start=1):
            raw_text = (page.extract_text() or "").strip()
            text = _clean_text(raw_text)
            if text:
                docs.append(
                    Document(
                        page_content=text,
                        metadata={"source": file_path.name, "page": page_num},
                    )
                )
        logger.info("pypdf: parsed and cleaned %d pages from '%s'", len(docs), file_path.name)
        return docs

    else:
        raise RuntimeError(
            "No PDF library available. Install PyMuPDF or pypdf: "
            "pip install PyMuPDF  OR  pip install pypdf"
        )


def _parse_text(file_path: Path) -> List[Document]:
    """Read and clean a plain text file as a single Document."""
    raw_text = file_path.read_text(encoding="utf-8", errors="replace").strip()
    text = _clean_text(raw_text)
    if not text:
        return []
    return [
        Document(
            page_content=text,
            metadata={"source": file_path.name, "page": None},
        )
    ]


# ── Public API ────────────────────────────────────────────────────────────────

def parse_document(file_path: Path) -> List[Document]:
    """
    Parse a document into raw LangChain Documents.
    Supports .pdf and plain text formats (.txt, .md, etc.).
    """
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(file_path)
    else:
        return _parse_text(file_path)


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Split Documents into smaller overlapping chunks for embedding.
    Prioritizes splitting on logical paragraph boundaries (\\n\\n) and
    sentence boundaries (. , ? , !) before falling back to spaces or characters.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", ". ", "? ", "! ", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    # Annotate with chunk index
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = idx

    logger.info("Split %d documents into %d chunks", len(documents), len(chunks))
    return chunks


def process_file(file_path: Path) -> List[Document]:
    """
    End-to-end: parse file → chunk.
    Returns a list of chunked LangChain Documents ready for embedding.
    """
    raw_docs = parse_document(file_path)
    if not raw_docs:
        raise ValueError(f"No text content could be extracted from '{file_path.name}'.")
    return chunk_documents(raw_docs)
