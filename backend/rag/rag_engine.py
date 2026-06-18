"""
RetailWise AI — RAG Engine
backend/rag/rag_engine.py

Builds a VectorStoreIndex from the 4 corpus JSON files using:
  - LlamaIndex (llama_index.core)
  - ChromaDB as the vector store (persisted to disk)
  - Gemini text-embedding-004 for embeddings

Functions:
  build_rag_index()  — load corpus → embed → persist to ChromaDB
  query_rag(question) -> dict  — retrieve top 3 chunks, return answer + source
"""

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────

_CORPUS_DIR = Path(__file__).parent / "corpus"
_CHROMA_DIR = Path(os.environ.get("CHROMA_PERSIST_DIR", str(Path(__file__).parent / "chroma_db")))

_CORPUS_FILES = [
    "festival_demand_patterns.json",
    "hartal_patterns.json",
    "supplier_playbooks.json",
    "retail_best_practices.json",
]

_GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
_COLLECTION_NAME = "retailwise_knowledge"
_TOP_K = 3

# Cache: index loaded once per process
_index_cache = None


# ── Document loader ───────────────────────────────────────────────────────────

def _load_corpus_documents():
    """
    Load all corpus JSON files and return a list of LlamaIndex Document objects.
    Each JSON entry becomes one Document with metadata.
    """
    from llama_index.core import Document

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
                # Prepend title to content for better retrieval signal
                full_text = f"# {title}\n\n{content}"
                documents.append(
                    Document(
                        text=full_text,
                        metadata={
                            "source": source_name,
                            "title": title,
                            "file": filename,
                        },
                    )
                )
            logger.info("[rag] Loaded %d entries from %s.", len(entries), filename)
        except Exception as exc:
            logger.error("[rag] Failed to load %s: %s", filename, exc)

    return documents


# ── Gemini embedding model ────────────────────────────────────────────────────

def _get_embed_model():
    """
    Return a LlamaIndex-compatible Gemini embedding model.
    Uses text-embedding-004 via google-generativeai.
    """
    try:
        from llama_index.embeddings.gemini import GeminiEmbedding
        return GeminiEmbedding(
            model_name="models/text-embedding-004",
            api_key=_GEMINI_API_KEY,
        )
    except ImportError:
        logger.warning(
            "[rag] llama_index.embeddings.gemini not found — "
            "falling back to local (mock) embeddings."
        )
        # Fallback: use LlamaIndex's default (will use a local model or raise)
        from llama_index.core import Settings
        return Settings.embed_model


# ── ChromaDB vector store ─────────────────────────────────────────────────────

def _get_chroma_vector_store():
    """Create or load the ChromaDB vector store collection."""
    import chromadb
    from llama_index.vector_stores.chroma import ChromaVectorStore

    _CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
    collection = client.get_or_create_collection(_COLLECTION_NAME)
    return ChromaVectorStore(chroma_collection=collection), client


# ── Build index ───────────────────────────────────────────────────────────────

def build_rag_index():
    """
    Load all corpus documents, embed them with Gemini text-embedding-004,
    and persist the index to ChromaDB.

    Idempotent: if the collection already has documents, skip re-embedding.
    Call this on startup and nightly (scheduler job at 02:00).
    """
    global _index_cache

    try:
        from llama_index.core import Settings, StorageContext, VectorStoreIndex

        embed_model = _get_embed_model()
        Settings.embed_model = embed_model
        Settings.llm = None  # We use Gemini directly — no LlamaIndex LLM calls

        vector_store, chroma_client = _get_chroma_vector_store()

        # Check if collection already has documents
        collection = chroma_client.get_or_create_collection(_COLLECTION_NAME)
        existing_count = collection.count()

        if existing_count > 0:
            logger.info(
                "[rag] ChromaDB already has %d documents — loading existing index.",
                existing_count,
            )
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_vector_store(
                vector_store,
                storage_context=storage_context,
            )
            _index_cache = index
            return index

        # Build fresh index
        documents = _load_corpus_documents()
        if not documents:
            logger.error("[rag] No corpus documents found. RAG will not function.")
            return None

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        logger.info("[rag] Embedding %d documents with Gemini text-embedding-004...", len(documents))

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=False,
        )
        _index_cache = index
        logger.info("[rag] ✅ RAG index built and persisted to %s.", _CHROMA_DIR)
        return index

    except Exception as exc:
        logger.error("[rag] build_rag_index failed: %s", exc)
        return None


def _get_or_build_index():
    """Return cached index, or build if not yet loaded."""
    global _index_cache
    if _index_cache is not None:
        return _index_cache
    return build_rag_index()


# ── Query function ────────────────────────────────────────────────────────────

def query_rag(question: str) -> dict:
    """
    Retrieve the top 3 most relevant knowledge chunks for the given question.
    Returns concatenated text and source metadata for the chat system prompt.

    Args:
        question: The user's chat question.

    Returns:
        {
            "answer": str,           # top-3 chunks concatenated with headers
            "source_document": str,  # comma-separated source names
            "num_chunks": int,
        }

    On any error: returns empty answer so chat still functions.
    """
    _empty = {"answer": "", "source_document": "knowledge base", "num_chunks": 0}

    if not question.strip():
        return _empty

    try:
        index = _get_or_build_index()
        if index is None:
            logger.warning("[rag] Index not available — returning empty RAG context.")
            return _empty

        retriever = index.as_retriever(similarity_top_k=_TOP_K)
        nodes = retriever.retrieve(question)

        if not nodes:
            return _empty

        chunks: list[str] = []
        sources: list[str] = []

        for node in nodes:
            text = node.node.get_content()
            source = node.node.metadata.get("source", "Knowledge Base")
            score = round(node.score, 3) if node.score else 0.0
            chunks.append(f"[Source: {source} | Relevance: {score}]\n{text}")
            if source not in sources:
                sources.append(source)

        return {
            "answer": "\n\n---\n\n".join(chunks),
            "source_document": ", ".join(sources),
            "num_chunks": len(chunks),
        }

    except Exception as exc:
        logger.error("[rag] query_rag failed: %s", exc)
        return _empty
