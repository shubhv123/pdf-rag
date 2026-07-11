"""
tests/test_upload.py
─────────────────────
Unit tests for POST /api/upload
"""
import io
import pytest
from fastapi.testclient import TestClient

# ── Minimal sample content ─────────────────────────────────────
SAMPLE_TEXT = b"""
Artificial Intelligence (AI) is intelligence demonstrated by machines.
It is a branch of computer science that aims to build smart machines
capable of performing tasks that typically require human intelligence.

Key applications include: natural language processing, computer vision,
robotics, and expert systems.
"""

SAMPLE_PDF_HEADER = b"%PDF-1.4"   # Minimal magic bytes for detection tests


# ── Fixtures ───────────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    """Create a TestClient for the FastAPI app."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from app.main import app
    return TestClient(app)


# ── Tests ──────────────────────────────────────────────────────

def test_health(client):
    """Health check endpoint should return 200."""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_upload_txt(client):
    """Uploading a .txt file should return 201 with a session_id."""
    file = io.BytesIO(SAMPLE_TEXT)
    r = client.post(
        "/api/upload",
        files={"file": ("sample.txt", file, "text/plain")},
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert "session_id" in data
    assert data["filename"] == "sample.txt"
    assert data["chunk_count"] >= 1


def test_upload_unsupported_type(client):
    """Uploading a .csv file should return 415."""
    file = io.BytesIO(b"col1,col2\nval1,val2")
    r = client.post(
        "/api/upload",
        files={"file": ("data.csv", file, "text/csv")},
    )
    assert r.status_code == 415


def test_upload_empty_file(client):
    """Uploading an empty file should return 422 (no content extracted)."""
    file = io.BytesIO(b"")
    r = client.post(
        "/api/upload",
        files={"file": ("empty.txt", file, "text/plain")},
    )
    assert r.status_code == 422  # HTTP_422_UNPROCESSABLE_CONTENT


def test_upload_returns_unique_session_ids(client):
    """Multiple uploads should produce different session_ids."""
    f1 = io.BytesIO(SAMPLE_TEXT)
    f2 = io.BytesIO(SAMPLE_TEXT + b"\nExtra content.")
    r1 = client.post("/api/upload", files={"file": ("a.txt", f1, "text/plain")})
    r2 = client.post("/api/upload", files={"file": ("b.txt", f2, "text/plain")})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["session_id"] != r2.json()["session_id"]
