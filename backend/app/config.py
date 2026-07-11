"""
backend/app/config.py
─────────────────────
Central settings loaded from .env using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent   # backend/


class Settings(BaseSettings):
    # ── HuggingFace ───────────────────────────────────────────────────────────
    hf_api_key: str = ""
    llm_model_id: str = "google/flan-t5-base"
    embedding_model_id: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── Chunking ──────────────────────────────────────────────────────────────
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # ── Retrieval ─────────────────────────────────────────────────────────────
    top_k: int = 2

    # ── Directories ───────────────────────────────────────────────────────────
    upload_dir: str = "uploads"
    vector_store_dir: str = "vector_store"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def upload_path(self) -> Path:
        p = BASE_DIR / self.upload_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def vector_store_path(self) -> Path:
        p = BASE_DIR / self.vector_store_dir
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
