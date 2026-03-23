from fastapi import HTTPException, status


class VectorStoreNotConfiguredError(RuntimeError):
    """Raised when the requested vector store backend is not properly configured."""


class LLMProviderError(RuntimeError):
    """Raised when there is an issue communicating with the LLM provider."""


class IngestionError(RuntimeError):
    """Raised when document ingestion fails."""


def raise_500(detail: str) -> None:
    """
    Convenience helper to raise a 500 HTTPException.
    """
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
    )