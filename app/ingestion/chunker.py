from typing import List, Dict, Optional


class TextChunker:
    """
    A text chunker used to break large documents into overlapping chunks
    based on WORD count to preserve semantic meaning.
    """

    def __init__(
            self,
            chunk_size_words: int = 200,
            chunk_overlap_words: int = 50,
    ):
        if chunk_overlap_words >= chunk_size_words:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size_words
        self.chunk_overlap = chunk_overlap_words

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Splits text into overlapping chunks based on words.
        """
        if not text or not text.strip():
            return []

        words = text.split()
        chunks = []
        start = 0
        chunk_id = 0

        base_metadata = metadata or {}

        while start < len(words):
            end = start + self.chunk_size
            chunk_txt = " ".join(words[start:end])

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_txt.strip(),
                "metadata": base_metadata
            })

            chunk_id += 1
            start += self.chunk_size - self.chunk_overlap

        return chunks

# Convenience function for pipeline usage
def chunk_text(
        text: str,
        chunk_size_words: int = 200,
        chunk_overlap_words: int = 50,
        metadata: Optional[Dict] = None
) -> List[Dict]:
    """
    Functional wrapper for quick usage in the ingestion pipeline.
    Passes word counts and metadata to the TextChunker.
    """
    chunker = TextChunker(
        chunk_size_words=chunk_size_words,
        chunk_overlap_words=chunk_overlap_words
    )
    return chunker.chunk_text(text, metadata=metadata)