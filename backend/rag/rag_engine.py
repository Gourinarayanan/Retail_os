"""
RetailWise AI — RAG Engine  (Pure Python TF-IDF edition)
backend/rag/rag_engine.py

Searches the 4 corpus JSON files using TF-IDF keyword matching.

NO external embedding API required — works 100% offline and reliably.
The Gemini LLM is still used for final answer generation via gemini_service;
this module only handles *retrieval* of relevant document chunks.

Functions:
  build_rag_index()  — load corpus, build TF-IDF index in memory
  query_rag(question) -> dict  — retrieve top-3 chunks, return answer + source
"""

import json
import logging
import math
import re
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────

_CORPUS_DIR = Path(__file__).parent / "corpus"

_CORPUS_FILES = [
    "festival_demand_patterns.json",
    "hartal_patterns.json",
    "supplier_playbooks.json",
    "retail_best_practices.json",
]

_TOP_K = 3

# ── In-memory index (built once at startup) ───────────────────────────────────

# List of dicts: {text, title, source}
_documents: list[dict] = []

# TF-IDF structures
_idf: dict[str, float] = {}         # term → IDF score
_doc_tf_idf: list[dict] = []        # per-doc {term: tfidf_score}

_index_ready = False


# ── Tokeniser ─────────────────────────────────────────────────────────────────

def _tokenise(text: str) -> list[str]:
    """Lowercase, remove punctuation, split on whitespace. Returns token list."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 2]


# ── TF-IDF builder ────────────────────────────────────────────────────────────

def _compute_tf(tokens: list[str]) -> dict[str, float]:
    counts: dict[str, int] = defaultdict(int)
    for t in tokens:
        counts[t] += 1
    total = len(tokens) or 1
    return {t: c / total for t, c in counts.items()}


def _build_tfidf_index(documents: list[dict]) -> tuple[dict, list[dict]]:
    """
    Build IDF table and per-document TF-IDF vectors.
    Returns (idf_dict, list_of_tfidf_dicts).
    """
    n = len(documents)
    # Document-frequency count
    df: dict[str, int] = defaultdict(int)
    token_lists = []
    for doc in documents:
        tokens = _tokenise(doc["text"])
        token_lists.append(tokens)
        for term in set(tokens):
            df[term] += 1

    # IDF = log((N + 1) / (df + 1)) + 1  (smoothed)
    idf = {term: math.log((n + 1) / (cnt + 1)) + 1.0 for term, cnt in df.items()}

    # Per-doc TF-IDF
    doc_tfidf = []
    for tokens in token_lists:
        tf = _compute_tf(tokens)
        tfidf = {term: tf_val * idf.get(term, 0.0) for term, tf_val in tf.items()}
        doc_tfidf.append(tfidf)

    return idf, doc_tfidf


def _cosine_similarity(query_vec: dict[str, float], doc_vec: dict[str, float]) -> float:
    """Cosine similarity between two sparse TF-IDF vectors."""
    dot = sum(query_vec.get(t, 0.0) * doc_vec.get(t, 0.0) for t in query_vec)
    norm_q = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0
    norm_d = math.sqrt(sum(v * v for v in doc_vec.values())) or 1.0
    return dot / (norm_q * norm_d)


# ── Corpus loader ─────────────────────────────────────────────────────────────

def _load_corpus() -> list[dict]:
    documents = []
    for filename in _CORPUS_FILES:
        filepath = _CORPUS_DIR / filename
        if not filepath.exists():
            logger.warning("[rag] Corpus file not found: %s — skipping.", filepath)
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                entries = json.load(f)
            source_name = filename.replace(".json", "").replace("_", " ").title()
            for entry in entries:
                title = entry.get("title", "Untitled")
                content = entry.get("content", "")
                if not content.strip():
                    continue
                documents.append({
                    "text": f"# {title}\n\n{content}",
                    "title": title,
                    "source": source_name,
                })
            logger.info("[rag] Loaded %d entries from %s.", len(entries), filename)
        except Exception as exc:
            logger.error("[rag] Failed to load %s: %s", filename, exc)
    return documents


# ── Public API ────────────────────────────────────────────────────────────────

def build_rag_index() -> bool:
    """
    Load all corpus JSON files and build an in-memory TF-IDF index.

    This is pure Python — no external API calls, no network dependency.
    Called once at startup and nightly by the scheduler.

    Returns True on success, False on failure.
    """
    global _documents, _idf, _doc_tf_idf, _index_ready

    try:
        docs = _load_corpus()
        if not docs:
            logger.error("[rag] No corpus documents found — RAG will not function.")
            return False

        idf, doc_tfidf = _build_tfidf_index(docs)

        _documents = docs
        _idf = idf
        _doc_tf_idf = doc_tfidf
        _index_ready = True

        logger.info(
            "[rag] ✅ TF-IDF index built: %d documents, %d unique terms.",
            len(docs),
            len(idf),
        )
        return True

    except Exception as exc:
        logger.error("[rag] build_rag_index failed: %s", exc)
        return False


def query_rag(question: str) -> dict:
    """
    Retrieve the top-3 most relevant knowledge chunks for the given question
    using TF-IDF cosine similarity.

    Args:
        question: The user's chat question.

    Returns:
        {
            "answer": str,           # top-3 chunks concatenated
            "source_document": str,  # comma-separated source names
            "num_chunks": int,
        }

    On any error or empty index: returns empty answer (chat still works via LLM).
    """
    _empty = {"answer": "", "source_document": "knowledge base", "num_chunks": 0}

    if not question.strip():
        return _empty

    if not _index_ready or not _documents:
        logger.warning("[rag] Index not ready — returning empty RAG context.")
        return _empty

    try:
        # Build query TF-IDF vector
        q_tokens = _tokenise(question)
        q_tf = _compute_tf(q_tokens)
        q_tfidf = {term: tf_val * _idf.get(term, 0.0) for term, tf_val in q_tf.items()}

        if not q_tfidf:
            return _empty

        # Score all documents
        scores = [
            _cosine_similarity(q_tfidf, doc_vec)
            for doc_vec in _doc_tf_idf
        ]

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:_TOP_K]

        # Filter out zero-score documents
        top_indices = [i for i in top_indices if scores[i] > 0.0]

        if not top_indices:
            return _empty

        chunks: list[str] = []
        sources: list[str] = []

        for idx in top_indices:
            doc = _documents[idx]
            score = round(scores[idx], 3)
            chunks.append(f"[Source: {doc['source']} | Relevance: {score}]\n{doc['text']}")
            if doc["source"] not in sources:
                sources.append(doc["source"])

        logger.debug("[rag] query matched %d chunks for: %.60s", len(chunks), question)

        return {
            "answer": "\n\n---\n\n".join(chunks),
            "source_document": ", ".join(sources),
            "num_chunks": len(chunks),
        }

    except Exception as exc:
        logger.error("[rag] query_rag failed: %s", exc)
        return _empty
