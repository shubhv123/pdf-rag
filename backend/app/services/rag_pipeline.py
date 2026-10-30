"""
backend/app/services/rag_pipeline.py
──────────────────────────────────────
RAG pipeline running the LLM fully LOCALLY on CPU using transformers.
Uses prompt conditioning and Beam Search to ensure descriptive, high-quality answers.
"""
import logging
from typing import Tuple, List
from functools import lru_cache

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.config import settings
from app.services.vector_store import load_store
from app.models.schemas import SourceChunk

logger = logging.getLogger(__name__)

# ── Local Model & Tokenizer Loader (Cached) ───────────────────────────────────

@lru_cache(maxsize=1)
def get_local_model_and_tokenizer() -> Tuple[AutoModelForSeq2SeqLM, AutoTokenizer]:
    """
    Load the Hugging Face model and tokenizer locally on CPU.
    Downloads them once on the first call and caches them in memory.
    """
    model_id = settings.llm_model_id  # default is google/flan-t5-base
    logger.info("Loading local LLM model: %s...", model_id)
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    
    # Put model in evaluation mode
    model.eval()
    logger.info("Local LLM model '%s' successfully loaded.", model_id)
    return model, tokenizer


# ── Prompt ────────────────────────────────────────────────────────────────────

QA_PROMPT_TEMPLATE = (
    "Use the context below to answer the question in a complete, detailed response.\n"
    "If the answer is not in the context, say 'I don't have enough information in the provided documents.'\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)


def _build_prompt(context: str, question: str) -> str:
    return QA_PROMPT_TEMPLATE.format(context=context, question=question)


def _call_llm(prompt: str) -> str:
    """Run inference locally on CPU using Beam Search for descriptive answers."""
    import torch
    model, tokenizer = get_local_model_and_tokenizer()
    logger.info("Running local beam search inference...")
    
    # Tokenize prompt
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Generate tokens (disable gradient calculation for speed/memory efficiency)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            num_beams=4,
            length_penalty=1.0,
        )
        
    # Decode and return
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer.strip()


# ── Public API ────────────────────────────────────────────────────────────────

def run_rag(session_id: str, question: str) -> Tuple[str, List[SourceChunk]]:
    """
    Execute the RAG pipeline for a given session and question.
    """
    # 1. Load vector store
    store = load_store(session_id)

    # 2. Retrieve top-k chunks with similarity search
    retriever = store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": settings.top_k,
        },
    )

    logger.info("Running RAG | session=%s | question=%s", session_id, question[:80])
    retrieved_docs = retriever.invoke(question)

    # 3. Build context string from retrieved chunks
    context = "\n\n---\n\n".join(doc.page_content for doc in retrieved_docs)

    # 4. Build prompt and call local LLM
    prompt = _build_prompt(context, question)
    
    try:
        answer = _call_llm(prompt)
    except Exception as e:
        logger.exception("Error during local LLM execution: %s", e)
        raise RuntimeError(f"Local LLM execution failed: {e}")

    # 5. Map source documents to response schema
    sources: List[SourceChunk] = [
        SourceChunk(
            content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
            page=doc.metadata.get("page"),
            chunk_index=doc.metadata.get("chunk_index"),
        )
        for doc in retrieved_docs
    ]

    logger.info("RAG complete | answer_len=%d | sources=%d", len(answer), len(sources))
    return answer, sources
