from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion.parsers.parser_factory import ParserFactory
from app.ingestion.chunker import chunk_text
from app.vectorstore.base import VectorStore
from app.core.config import settings
from app.ingestion.parsers.exceptions import ParserError
from app.vectorstore.exceptions import VectorStoreError
import uuid

router = APIRouter()

# Vector store instance (FAISS, Chroma, Qdrant, or in-memory)
vector_store = VectorStore.get_store(settings.VECTOR_DB_BACKEND)


@router.post("/")
async def upload_documents(files: list[UploadFile] = File(...)):
    """
    Upload multiple documents, parse, chunk, embed, and store each.
    Returns per-file success or error.
    """

    results = []

    for file in files:
        try:
            # -------------------------
            # Read file bytes
            # -------------------------
            try:
                file_bytes = await file.read()
            except Exception:
                results.append({
                    "filename": file.filename,
                    "error": "Failed to read file bytes (possibly corrupted upload)"
                })
                continue

            # -------------------------
            # Parse document
            # -------------------------
            try:
                parser = ParserFactory.get_parser(file.filename)
                text = parser.parse(file_bytes)
            except ParserError as e:
                results.append({
                    "filename": file.filename,
                    "error": f"Parser error: {str(e)}"
                })
                continue
            except UnicodeDecodeError:
                results.append({
                    "filename": file.filename,
                    "error": "Unsupported file encoding"
                })
                continue

            # -------------------------
            # Guard: No extracted text
            # -------------------------
            if not text or not text.strip():
                results.append({
                    "filename": file.filename,
                    "error": "No text extracted — possibly scanned image or empty file."
                })
                continue

            # -------------------------
            # Chunk text
            # -------------------------
            try:
                chunks = chunk_text(text)
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "error": f"Chunking error: {str(e)}"
                })
                continue

            # -------------------------
            # Guard: No chunks
            # -------------------------
            if not chunks:
                results.append({
                    "filename": file.filename,
                    "error": "Chunking produced no output — skipping embedding."
                })
                continue

            # -------------------------
            # Store in vector DB
            # -------------------------
            document_id = str(uuid.uuid4())

            try:
                vector_store.add_document(
                    document_id=document_id,
                    chunks=chunks,
                    metadata={"filename": file.filename}
                )
            except VectorStoreError as e:
                results.append({
                    "filename": file.filename,
                    "error": f"Vector store error: {str(e)}"
                })
                continue

            # -------------------------
            # Success
            # -------------------------
            results.append({
                "filename": file.filename,
                "document_id": document_id,
                "chunks": len(chunks)
            })

        except Exception as e:
            # Final fallback — should rarely trigger
            results.append({
                "filename": file.filename,
                "error": f"Unexpected error: {str(e)}"
            })

    return {"results": results}

@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    vector_store.delete_document(doc_id)
    return {"status": "deleted"}
