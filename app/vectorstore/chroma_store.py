import chromadb
from app.core.config import settings
from .base import BaseVectorStore, OpenAIEmbedder


class ChromaVectorStore(BaseVectorStore):
    def __init__(self):
        self.embedder = OpenAIEmbedder()

        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(self, document_id, chunks, metadata=None):
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_batch(texts)

        ids = [f"{document_id}:{c.get('chunk_id')}" for c in chunks]
        metadatas = []

        for chunk in chunks:
            meta = {
                **(metadata or {}),
                **chunk.get("metadata", {}),
                "document_id": document_id,
                "chunk_id": chunk.get("chunk_id"),
            }
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

    def search(self, query, top_k=5, document_ids=None):
        query_emb = self.embedder.embed_text(query)

        where = {}
        if document_ids:
            where["document_id"] = {"$in": document_ids}

        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            where=where or None,
        )

        hits = []
        for doc, meta, dist in zip(
            results.get("documents", [[]])[0],
            results.get("metadatas", [[]])[0],
            results.get("distances", [[]])[0],
        ):
            hits.append(
                {
                    "text": doc,
                    "score": float(1 - dist),
                    "metadata": meta,
                }
            )

        return hits

    def delete_document(self, doc_id: str):
        self.collection.delete(where={"document_id": doc_id})
