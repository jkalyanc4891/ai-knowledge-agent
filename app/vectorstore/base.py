from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.exceptions import VectorStoreNotConfiguredError


class BaseVectorStore(ABC):
    """
    Abstract base class for all vector store backends.
    """

    @abstractmethod
    def add_document(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store chunks for a document.
        Each chunk dict must contain at least: {"text": str, "chunk_id": int, "metadata": dict}
        """
        ...

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks.
        Returns list of dicts: {"text": str, "score": float, "metadata": dict}
        """
        ...


class OpenAIEmbedder:
    """
    Thin wrapper around OpenAI embeddings.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL

    def embed_text(self, text: str) -> List[float]:
        resp = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return resp.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [d.embedding for d in resp.data]


class VectorStore:
    """
    Factory / registry for vector store backends.
    """

    _instance: Optional[BaseVectorStore] = None

    @classmethod
    def get_store(cls, backend: str) -> BaseVectorStore:
        if cls._instance is not None:
            return cls._instance

        backend = backend.lower()

        if backend == "in_memory":
            from .in_memory import InMemoryVectorStore
            cls._instance = InMemoryVectorStore()
        elif backend == "chroma":
            from .chroma_store import ChromaVectorStore
            cls._instance = ChromaVectorStore()
        else:
            raise VectorStoreNotConfiguredError(
                f"Unsupported or unconfigured vector store backend: {backend}"
            )

        return cls._instance