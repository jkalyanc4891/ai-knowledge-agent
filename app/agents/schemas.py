from pydantic import BaseModel, Field, field_validator
from typing import List

class PlanSchema(BaseModel):
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