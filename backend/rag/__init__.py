"""RAG package — LlamaIndex + ChromaDB knowledge retrieval for RetailWise AI."""

from rag.rag_engine import build_rag_index, query_rag

__all__ = ["build_rag_index", "query_rag"]
