from typing import List, Dict, Any, Optional
import math

from .base import BaseVectorStore, OpenAIEmbedder


class InMemoryVectorStore(BaseVectorStore):
    """
    Simple in-memory vector store for development and testing.
    Not for large-scale production, but great for local runs.
    """

    def __init__(self):
        self.embedder = OpenAIEmbedder()
        # {document_id: [{"embedding": [...], "text": str, "metadata": dict}]}
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def add_document(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        doc_entries: List[Dict[str, Any]] = []

        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_batch(texts)

        for chunk, emb in zip(chunks, embeddings):
            entry = {
                "embedding": emb,
                "text": chunk["text"],
                "metadata": {
                    **(metadata or {}),
                    **chunk.get("metadata", {}),
                    "document_id": document_id,
                    "chunk_id": chunk.get("chunk_id"),
                },
            }
            doc_entries.append(entry)

        self._store.setdefault(document_id, []).extend(doc_entries)

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        if not self._store:
            return []

        query_emb = self.embedder.embed_text(query)

        candidates: List[Dict[str, Any]] = []
        target_docs = document_ids or list(self._store.keys())

        for doc_id in target_docs:
            for entry in self._store.get(doc_id, []):
                score = self._cosine_similarity(query_emb, entry["embedding"])
                candidates.append(
                    {
                        "text": entry["text"],
                        "score": float(score),
                        "metadata": entry["metadata"],
                    }
                )

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def delete_document(self, doc_id: str):
        pass
