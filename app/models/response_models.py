from typing import List, Dict, Any
from pydantic import BaseModel, Field


class SourceChunk(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = Field(default_factory=list)
    confidence: float | None = Field(
        default=None,
        description="Optional confidence score from agent/validator.",
    )