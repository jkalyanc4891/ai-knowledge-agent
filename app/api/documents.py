from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ingestion.parsers.parser_factory import ParserFactory
from app.ingestion.chunker import chunk_text
from app.vectorstore.base import VectorStore
from app.core.config import settings
import uuid

router = APIRouter()

# Vector store instance (FAISS, Chroma, Qdrant, or in-memory)
vector_store = VectorStore.get_store(settings.VECTOR_DB_BACKEND)


@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a document, parses it, chunks it, embeds it, and stores it in the vector DB.
    """

    try:
        file_bytes = await file.read()

        parser = ParserFactory.get_parser(file.filename)
        text = parser.parse(file_bytes)

        chunks = chunk_text(text)

        document_id = str(uuid.uuid4())

        vector_store.add_document(
            document_id=document_id,
            chunks=chunks,
            metadata={"filename": file.filename}
        )

        return {"document_id": document_id, "chunks": len(chunks)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    vector_store.delete_document(doc_id)
    return {"status": "deleted"}
