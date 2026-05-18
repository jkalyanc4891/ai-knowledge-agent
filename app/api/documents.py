from fastapi import APIRouter, UploadFile, File, HTTPException, status
import logging
import uuid

from app.ingestion.parsers.parser_factory import ParserFactory
from app.ingestion.chunker import chunk_text
from app.vectorstore.base import VectorStore
from app.core.config import settings
from app.core.exceptions import (
    VectorStoreNotConfiguredError,
    VectorStoreError,
    IngestionError,
    ParserError,
    ChunkingError,
    EmbeddingError,
    DocumentNotFoundError,
)

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


try:
    # Vector store instance: FAISS, Chroma, Qdrant, or in-memory
    vector_store = VectorStore.get_store(settings.VECTOR_DB_BACKEND)

except VectorStoreNotConfiguredError as e:
    logger.critical("Vector store backend is not configured correctly: %s", e)
    raise

except VectorStoreError as e:
    logger.critical("Vector store initialization failed: %s", e)
    raise

except Exception:
    logger.exception("Unexpected error while initializing vector store")
    raise


@router.post("/")
async def upload_documents(files: list[UploadFile] = File(...)):
    """
    Upload multiple documents, parse, chunk, embed, and store each.
    Returns per-file success or error.
    """

    if not files:
        logger.warning("Upload request received with no files.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required.",
        )

    results = []

    for file in files:
        filename = file.filename or "unknown"

        try:
            logger.info("Starting ingestion for file: %s", filename)

            # -------------------------
            # Guard: Validate filename
            # -------------------------
            if not file.filename:
                logger.warning("Skipping uploaded file with missing filename.")
                results.append({
                    "filename": filename,
                    "error": "Uploaded file is missing a filename.",
                })
                continue

            # -------------------------
            # Read file bytes
            # -------------------------
            try:
                file_bytes = await file.read()

            except OSError as e:
                logger.warning("Failed to read uploaded file bytes for %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": "Failed to read file bytes.",
                })
                continue

            except RuntimeError as e:
                logger.warning("Runtime error while reading uploaded file %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": "Failed to read uploaded file stream.",
                })
                continue

            if not file_bytes:
                logger.warning("Uploaded file is empty: %s", filename)
                results.append({
                    "filename": filename,
                    "error": "Uploaded file is empty.",
                })
                continue

            # -------------------------
            # Parse document
            # -------------------------
            try:
                parser = ParserFactory.get_parser(filename)
                text = parser.parse(file_bytes)

            except ParserError as e:
                logger.warning("Parser error for file %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": f"Parser error: {str(e)}",
                })
                continue

            except UnicodeDecodeError as e:
                logger.warning("Unsupported encoding for file %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": "Unsupported file encoding.",
                })
                continue

            except ValueError as e:
                logger.warning("Unsupported or invalid file type for %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": str(e),
                })
                continue

            except Exception as e:
                logger.exception("Unexpected parsing failure for file %s", filename)
                results.append({
                    "filename": filename,
                    "error": "Unexpected error while parsing document.",
                })
                continue

            # -------------------------
            # Guard: No extracted text
            # -------------------------
            if not text or not text.strip():
                logger.warning(
                    "No text extracted from file %s. File may be empty, scanned, or unsupported.",
                    filename,
                )
                results.append({
                    "filename": filename,
                    "error": "No text extracted — possibly scanned image or empty file.",
                })
                continue

            # -------------------------
            # Chunk text
            # -------------------------
            try:
                chunks = chunk_text(text)

            except ChunkingError as e:
                logger.warning("Chunking error for file %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": f"Chunking error: {str(e)}",
                })
                continue

            except ValueError as e:
                logger.warning("Invalid text input while chunking file %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": str(e),
                })
                continue

            except Exception as e:
                logger.exception("Unexpected chunking failure for file %s", filename)
                results.append({
                    "filename": filename,
                    "error": "Unexpected error while chunking document.",
                })
                continue

            # -------------------------
            # Guard: No chunks
            # -------------------------
            if not chunks:
                logger.warning("Chunking produced no output for file: %s", filename)
                results.append({
                    "filename": filename,
                    "error": "Chunking produced no output — skipping embedding.",
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
                    metadata={"filename": filename},
                )

            except EmbeddingError as e:
                logger.error("Embedding generation failed for file %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": "Embedding generation failed.",
                })
                continue

            except VectorStoreError as e:
                logger.error("Vector store error while storing file %s: %s", filename, e)
                results.append({
                    "filename": filename,
                    "error": f"Vector store error: {str(e)}",
                })
                continue

            except Exception:
                logger.exception("Unexpected vector store failure for file %s", filename)
                results.append({
                    "filename": filename,
                    "error": "Unexpected error while storing document.",
                })
                continue

            # -------------------------
            # Success
            # -------------------------
            logger.info(
                "Successfully ingested file %s with document_id=%s and chunks=%s",
                filename,
                document_id,
                len(chunks),
            )

            results.append({
                "filename": filename,
                "document_id": document_id,
                "chunks": len(chunks),
            })

        except IngestionError as e:
            logger.error("Ingestion error for file %s: %s", filename, e)
            results.append({
                "filename": filename,
                "error": "Document ingestion failed.",
            })

        except Exception:
            # Final fallback — should rarely trigger
            logger.exception("Unexpected ingestion failure for file %s", filename)
            results.append({
                "filename": filename,
                "error": "Unexpected error while processing file.",
            })

    return {"results": results}


@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    """
    Delete a document from the vector store.
    """

    try:
        if not doc_id or not doc_id.strip():
            logger.warning("Delete request received with empty document id.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document id is required.",
            )

        vector_store.delete_document(doc_id)

        logger.info("Successfully deleted document_id=%s", doc_id)

        return {"status": "deleted"}

    except HTTPException:
        raise

    except DocumentNotFoundError as e:
        logger.warning("Document not found during delete. document_id=%s error=%s", doc_id, e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except VectorStoreError as e:
        logger.error("Vector store error while deleting document_id=%s: %s", doc_id, e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store operation failed while deleting document.",
        )

    except Exception:
        logger.exception("Unexpected error while deleting document_id=%s", doc_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected backend error while deleting document.",
        )