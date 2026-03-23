from typing import List, Dict, Optional


class TextChunker:
    """
    A text chunker used to break large documents into overlapping chunks suitable for embedding and semantic search.
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[Dict]:
        """
        Splits text into overlapping chunks.

        Returns a list of dictionaries:
        [
            { "chunk_id": int, "text": str }
        ]
        """
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_txt = text[start:end]

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_txt.strip()
            })

            chunk_id += 1
            start += self.chunk_size - self.chunk_overlap

        return chunks


# Convenience function for pipeline usage
def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 200) -> List[Dict]:
    """
    Functional wrapper for quick usage in ingestion pipeline.
    """
    return TextChunker(chunk_size, chunk_overlap).chunk_text(text)