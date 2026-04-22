from .parsers.parser_factory import ParserFactory
from .chunker import chunk_text


def ingest_file(filename: str, file_bytes: bytes):
    parser = ParserFactory.get_parser(filename)
    text = parser.parse(file_bytes)

    # Document-level metadata
    metadata = {
        "document_id": filename,
        "source": filename,
        "file_type": filename.split(".")[-1]
    }

    # Use your new word-based chunker
    chunks = chunk_text(
        text,
        chunk_size_words=200,
        chunk_overlap_words=50,
        metadata=metadata
    )

    return {
        "document_id": filename,
        "chunks": chunks
    }
