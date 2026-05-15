from typing import Dict, Any, List
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str | None = None
    content_type: str | None = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    chunk_id: int
    document_id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestedDocument(BaseModel):
    document_id: str
    chunks: List[DocumentChunk]
    metadata: DocumentMetadata