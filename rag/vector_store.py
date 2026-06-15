import re
import math
from typing import List, Dict, Any

# Simple TF-IDF Vector Store for semantic retrieval
class SimpleVectorStore:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.vocab = {}
        self.idf = {}
        self.tf_vectors = []

    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """
        Adds list of documents with optional metadata.
        """
        if metadata is None:
            metadata = [{} for _ in documents]
            
        for doc, meta in zip(documents, metadata):
            self.documents.append(doc)
            self.metadata.append(meta)
            
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        words = re.findall(r'\b[a-z0-9]+\b', text)
        return words

    def _build_index(self):
        self.vocab = {}
        self.tf_vectors = []
        doc_count = len(self.documents)
        
        for doc in self.documents:
            words = self._tokenize(doc)
            tf = {}
            for w in words:
                tf[w] = tf.get(w, 0) + 1
            self.tf_vectors.append(tf)
            for w in tf:
                self.vocab[w] = self.vocab.get(w, 0) + 1
                
        self.idf = {}
        for w, df in self.vocab.items():
            self.idf[w] = math.log((1 + doc_count) / (1 + df)) + 1

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """
        Searches the vector store using cosine similarity of TF-IDF vectors.
        """
        if not self.documents:
            return []
            
        query_words = self._tokenize(query)
        if not query_words:
            return [{"document": self.documents[i], "metadata": self.metadata[i], "score": 0.0} for i in range(min(top_k, len(self.documents)))]
            
        query_tf = {}
        for w in query_words:
            query_tf[w] = query_tf.get(w, 0) + 1
            
        query_vector = {}
        query_norm_sq = 0.0
        for w, tf_val in query_tf.items():
            if w in self.vocab:
                val = tf_val * self.idf[w]
                query_vector[w] = val
                query_norm_sq += val * val
        query_norm = math.sqrt(query_norm_sq)
        
        if query_norm == 0:
            return [{"document": self.documents[i], "metadata": self.metadata[i], "score": 0.0} for i in range(min(top_k, len(self.documents)))]
            
        results = []
        for idx, tf_dict in enumerate(self.tf_vectors):
            dot_product = 0.0
            doc_norm_sq = 0.0
            
            for w in self.vocab:
                tf_val = tf_dict.get(w, 0)
                doc_val = tf_val * self.idf[w]
                doc_norm_sq += doc_val * doc_val
                if w in query_vector:
                    dot_product += query_vector[w] * doc_val
                    
            doc_norm = math.sqrt(doc_norm_sq)
            similarity = 0.0
            if doc_norm > 0:
                similarity = dot_product / (query_norm * doc_norm)
                
            results.append({
                "document": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": round(similarity, 4)
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


# 1. Festival RAG (festival_rag)
festival_rag = SimpleVectorStore()
festival_rag.add_documents(
    documents=[
        "Diwali: FMCG category snacks. Demand Multiplier: 1.48 (+48%). Nationwide surge in retail purchasing.",
        "Onam: FMCG category Banana Chips. Demand Multiplier: 1.42 (+42%). High local demand in Kerala."
    ],
    metadata=[
        {"festival": "Diwali", "category": "Snacks", "multiplier": 1.48},
        {"festival": "Onam", "category": "Banana Chips", "multiplier": 1.42}
    ]
)

# 2. Hartal RAG (hartal_rag)
hartal_rag = SimpleVectorStore()
hartal_rag.add_documents(
    documents=[
        "Before Hartal (pre-strike): Customers panic buy to stock up. Demand Multiplier: 1.65 (+65% surge).",
        "During Hartal (strike day): Complete commercial shutdown. Demand Multiplier: 0.10 (-90% drop).",
        "After Hartal (post-strike): Market reopening recovery. Demand Multiplier: 1.15 (+15% bump)."
    ],
    metadata=[
        {"timing": "Before Hartal", "multiplier": 1.65},
        {"timing": "During Hartal", "multiplier": 0.10},
        {"timing": "After Hartal", "multiplier": 1.15}
    ]
)

# 3. Supplier RAG (supplier_rag)
supplier_rag = SimpleVectorStore()
supplier_rag.add_documents(
    documents=[
        "Supplier A: Price score: 95. On-time delivery rate: 92%. Complaints: 2. Average lead time: 5 days.",
        "Supplier B: Price score: 84. On-time delivery rate: 61%. Complaints: 11. Average lead time: 4 days.",
        "Supplier C: Price score: 90. On-time delivery rate: 98%. Complaints: 1. Average lead time: 2 days."
    ],
    metadata=[
        {"supplier": "Supplier A", "price_score": 95, "reliability_score": 92, "speed_score": 50, "lead_time_days": 5}, # speed_score: 50
        {"supplier": "Supplier B", "price_score": 84, "reliability_score": 61, "speed_score": 60, "lead_time_days": 4}, # speed_score: 60
        {"supplier": "Supplier C", "price_score": 90, "reliability_score": 98, "speed_score": 90, "lead_time_days": 2}  # speed_score: 90 (2 days lead time)
    ]
)
