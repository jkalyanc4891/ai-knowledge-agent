from .parsers.parser_factory import ParserFactory
from .chunker import chunk_text

def ingest_file(filename: str, file_bytes: bytes):
    parser = ParserFactory.get_parser(filename)
    text = parser.parse(file_bytes)

    chunks = chunk_text(text)

    return {
        "document_id": filename,  # or UUID
        "chunks": chunks
    }