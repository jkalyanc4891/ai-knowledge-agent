from typing import List, Dict, Any
from app.vectorstore.base import BaseVectorStore


class RetrievalAgent:
    """
    Specialized retrieval agent that:
    - Executes the retrieval plan
    - Fetches relevant chunks from the vector store
    """

    def __init__(self, vector_store: BaseVectorStore):
        self.vector_store = vector_store

    def retrieve(self, query: str, document_ids: List[str], top_k: int) -> List[Dict[str, Any]]:
        if top_k is None or top_k <= 0:
            top_k = 5

        return self.vector_store.search(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
        )
