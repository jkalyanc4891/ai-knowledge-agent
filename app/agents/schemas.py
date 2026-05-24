from pydantic import BaseModel, Field, field_validator
from typing import List

class AgentPlan(BaseModel):
    """
    Validated retrieval plan for the agentic RAG workflow
    This model is useful when parsing LLM-generated plans,
    because it provides a deterministic schema and safe
    defaults for downstream pipeline execution.
    """
    retrieve: bool = Field(default=True)
    top_k: int = Field(default=5, ge=1)  # ge=1 ensures top_k is >= 1
    documents: List[str] = Field(default_factory=list)

    @field_validator("top_k", mode="before")
    @classmethod
    def ensure_int(cls, v):
        try:
            return int(v)
        except (ValueError, TypeError):
            return 5 # Fallback to default