from fastapi import HTTPException, status


class AppError(RuntimeError):
    """Base class for application-specific runtime errors."""


class VectorStoreNotConfiguredError(AppError):
    """Raised when the requested vector store backend is not properly configured."""


class VectorStoreError(AppError):
    """Raised when a vector store operation fails."""


class RetrievalError(AppError):
    """Raised when document retrieval from the vector store fails."""


class DocumentNotFoundError(AppError):
    """Raised when one or more requested documents cannot be found."""


class LLMProviderError(AppError):
    """Raised when there is an issue communicating with the LLM provider."""


class LLMResponseError(AppError):
    """Raised when the LLM returns an invalid, empty, or unusable response."""


class AgentOrchestrationError(AppError):
    """Raised when the agent orchestration process fails."""


class AgentResponseError(AppError):
    """Raised when the agent returns a malformed response contract."""


class AgentTimeoutError(AppError):
    """Raised when the agent or one of its downstream services times out."""


class IngestionError(AppError):
    """Raised when document ingestion fails."""


class ParserError(IngestionError):
    """Raised when document parsing fails."""


class ChunkingError(IngestionError):
    """Raised when document chunking fails."""


class EmbeddingError(IngestionError):
    """Raised when embedding generation fails."""


def raise_400(detail: str) -> None:
    """Convenience helper to raise a 400 HTTPException."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def raise_404(detail: str) -> None:
    """Convenience helper to raise a 404 HTTPException."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def raise_500(detail: str) -> None:
    """Convenience helper to raise a 500 HTTPException."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
    )


def raise_502(detail: str) -> None:
    """Convenience helper to raise a 502 HTTPException."""
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=detail,
    )


def raise_503(detail: str) -> None:
    """Convenience helper to raise a 503 HTTPException."""
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail,
    )


def raise_504(detail: str) -> None:
    """Convenience helper to raise a 504 HTTPException."""
    raise HTTPException(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        detail=detail,
    )


def to_http_exception(exc: Exception) -> HTTPException:
    """
    Convert application exceptions into appropriate HTTPException responses.
    """

    if isinstance(exc, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if isinstance(exc, DocumentNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    if isinstance(exc, AgentTimeoutError):
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI agent timed out while processing the request.",
        )

    if isinstance(exc, RetrievalError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve relevant document context.",
        )

    if isinstance(exc, VectorStoreNotConfiguredError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector store is not properly configured.",
        )

    if isinstance(exc, VectorStoreError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store operation failed.",
        )

    if isinstance(exc, LLMProviderError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider failed while generating the answer.",
        )

    if isinstance(exc, LLMResponseError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider returned an invalid response.",
        )

    if isinstance(exc, AgentResponseError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    if isinstance(exc, AgentOrchestrationError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The AI agent failed while processing the request.",
        )

    if isinstance(exc, ParserError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to parse the uploaded document.",
        )

    if isinstance(exc, ChunkingError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to chunk the uploaded document.",
        )

    if isinstance(exc, EmbeddingError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate embeddings for the document.",
        )

    if isinstance(exc, IngestionError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document ingestion failed.",
        )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected backend error.",
    )