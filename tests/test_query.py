"""
tests/test_query.py
─────────────────────
Unit tests for POST /api/query
"""
import io
import pytest
from fastapi.testclient import TestClient

SAMPLE_TEXT = b"""
The Python programming language was created by Guido van Rossum.
Python is known for its clean and readable syntax.
It supports multiple programming paradigms including procedural,
object-oriented, and functional programming.
Python 3.0 was released in 2008 and introduced many breaking changes
compared to Python 2, including better Unicode support.
"""


@pytest.fixture(scope="module")
def client_with_session():
    """
    Creates a TestClient and uploads a sample document.
    Returns (client, session_id).
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from app.main import app
    client = TestClient(app)

    file = io.BytesIO(SAMPLE_TEXT)
    r = client.post(
        "/api/upload",
        files={"file": ("python_info.txt", file, "text/plain")},
    )
    assert r.status_code == 201, f"Upload failed: {r.text}"
    session_id = r.json()["session_id"]
    return client, session_id


def test_query_missing_session(client_with_session):
    """Query with a non-existent session_id should return 404."""
    client, _ = client_with_session
    r = client.post(
        "/api/query",
        json={"session_id": "00000000-0000-0000-0000-000000000000", "question": "Who created Python?"},
    )
    assert r.status_code == 404


def test_query_short_question(client_with_session):
    """Question shorter than 3 characters should return 422."""
    client, session_id = client_with_session
    r = client.post(
        "/api/query",
        json={"session_id": session_id, "question": "Hi"},
    )
    assert r.status_code == 422


def test_query_returns_answer_and_sources(client_with_session):
    """
    A valid question should return an answer string and at least one source chunk.
    NOTE: This test requires HF_API_KEY to be set. Skip if not configured.
    """
    import os
    if not os.getenv("HF_API_KEY"):
        pytest.skip("HF_API_KEY not set — skipping LLM test")

    client, session_id = client_with_session
    r = client.post(
        "/api/query",
        json={"session_id": session_id, "question": "Who created the Python programming language?"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "sources" in data
    assert len(data["sources"]) >= 1
    # Each source should have required fields
    for src in data["sources"]:
        assert "content" in src
        assert "source" in src


def test_query_response_schema(client_with_session):
    """Response should always include question, answer, and sources keys."""
    import os
    if not os.getenv("HF_API_KEY"):
        pytest.skip("HF_API_KEY not set — skipping LLM test")

    client, session_id = client_with_session
    r = client.post(
        "/api/query",
        json={"session_id": session_id, "question": "What is Python 3.0?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) >= {"question", "answer", "sources"}
    assert data["question"] == "What is Python 3.0?"
