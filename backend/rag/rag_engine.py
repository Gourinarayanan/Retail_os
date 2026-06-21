"""
RetailWise AI — RAG Engine (ChromaDB Vector Edition)
backend/rag/rag_engine.py

Uses ChromaDB for true semantic Vector Search.
"""

import json
import logging
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────

_CORPUS_DIR = Path(__file__).parent / "corpus"
_CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"

_CORPUS_FILES = [f.name for f in _CORPUS_DIR.glob("*.json")]

_TOP_K = 3
_COLLECTION_NAME = "retailwise_knowledge"

# ── Globals ───────────────────────────────────────────────────────────────────

_chroma_client = None
_collection = None
_index_ready = False

# We'll use Gemini for embeddings to save RAM on the Free Tier
_embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.environ.get("GEMINI_API_KEY", ""),
    model_name="models/text-embedding-004"
)

# ── Corpus loader ─────────────────────────────────────────────────────────────

def _load_corpus() -> list[dict]:
    documents = []
    doc_id = 0
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
                
                doc_id += 1
                documents.append({
                    "id": f"doc_{doc_id}",
                    "text": f"# {title}\n\n{content}",
                    "metadata": {"title": title, "source": source_name},
                })
            logger.info("[rag] Loaded %d entries from %s.", len(entries), filename)
        except Exception as exc:
            logger.error("[rag] Failed to load %s: %s", filename, exc)
    return documents


# ── Public API ────────────────────────────────────────────────────────────────

def build_rag_index() -> bool:
    """
    Load all corpus JSON files and build/update the ChromaDB collection.
    Called once at startup.
    Returns True on success, False on failure.
    """
    global _chroma_client, _collection, _index_ready

    try:
        # Initialize Persistent Chroma Client
        _CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=str(_CHROMA_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        _collection = _chroma_client.get_or_create_collection(
            name=_COLLECTION_NAME,
            embedding_function=_embedding_fn
        )
        
        # Check if already populated to save time on restart
        if _collection.count() > 0:
            logger.info("[rag] ✅ ChromaDB index already populated with %d documents.", _collection.count())
            _index_ready = True
            return True

        # If empty, load from JSON and insert
        logger.info("[rag] ChromaDB collection is empty. Embedding JSON corpus...")
        docs = _load_corpus()
        if not docs:
            logger.error("[rag] No corpus documents found — RAG will not function.")
            return False

        # Prepare arrays for Chroma
        ids = [d["id"] for d in docs]
        texts = [d["text"] for d in docs]
        metadatas = [d["metadata"] for d in docs]
        
        # Add to Chroma (this will trigger the embedding download & compute on first run)
        _collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

        _index_ready = True
        logger.info("[rag] ✅ ChromaDB index built: %d documents embedded successfully.", len(docs))
        return True

    except Exception as exc:
        logger.error("[rag] build_rag_index failed: %s", exc)
        return False


def query_rag(question: str) -> dict:
    """
    Retrieve the top-K most relevant knowledge chunks using ChromaDB semantic search.
    """
    _empty = {"answer": "", "source_document": "knowledge base", "num_chunks": 0}

    if not question.strip():
        return _empty

    if not _index_ready or _collection is None:
        logger.warning("[rag] Chroma index not ready — returning empty RAG context.")
        return _empty

    try:
        results = _collection.query(
            query_texts=[question],
            n_results=_TOP_K
        )
        
        # Extract matches
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        if not documents:
            return _empty

        chunks: list[str] = []
        sources: list[str] = []

        for doc, meta, dist in zip(documents, metadatas, distances):
            source = meta.get("source", "Unknown")
            # Distance in Chroma default (L2) — lower is better. 
            chunks.append(f"[Source: {source} | L2 Distance: {dist:.3f}]\n{doc}")
            if source not in sources:
                sources.append(source)

        logger.debug("[rag] query matched %d chunks for: %.60s", len(chunks), question)

        return {
            "answer": "\n\n---\n\n".join(chunks),
            "source_document": ", ".join(sources),
            "num_chunks": len(chunks),
        }

    except Exception as exc:
        logger.error("[rag] query_rag failed: %s", exc)
        return _empty
