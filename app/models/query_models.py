from typing import List
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question.")
    document_ids: List[str] = Field(
        default_factory=list,
        description="Optional list of document IDs to restrict retrieval to.",
    )