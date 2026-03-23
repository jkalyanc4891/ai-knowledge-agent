from typing import List, Dict, Any
from app.vectorstore.base import BaseVectorStore


class RAGRetriever:
    """
    Thin wrapper around the vector store to retrieve relevant chunks
    for a given query and optional document filters.
    """

    def __init__(self, vector_store: BaseVectorStore, top_k: int = 5):
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        document_ids: List[str] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of retrieved chunks with metadata.

        Each item:
        {
            "text": str,
            "score": float,
            "metadata": dict
        }
        """
        results = self.vector_store.search(
            query=query,
            top_k=self.top_k,
            document_ids=document_ids,
        )
        return results