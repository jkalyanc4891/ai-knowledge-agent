from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging

from app.rag.pipeline import RAGPipeline
from app.agents.orchestrator import AgentOrchestrator
from app.vectorstore.base import VectorStore
from app.core.config import settings
from app.core.exceptions import (
    AppError,
    VectorStoreNotConfiguredError,
    VectorStoreError,
    RetrievalError,
    DocumentNotFoundError,
    LLMProviderError,
    LLMResponseError,
    AgentOrchestrationError,
    AgentResponseError,
    AgentTimeoutError,
    to_http_exception,
)

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


try:
    vector_store = VectorStore.get_store(settings.VECTOR_DB_BACKEND)
    rag_pipeline = RAGPipeline(vector_store)
    agent_orchestrator = AgentOrchestrator(rag_pipeline, vector_store)

except VectorStoreNotConfiguredError as e:
    logger.critical("Vector store backend is not configured correctly: %s", e)
    raise

except VectorStoreError as e:
    logger.critical("Vector store initialization failed: %s", e)
    raise

except Exception:
    logger.exception("Unexpected error while initializing query dependencies")
    raise


class QueryRequest(BaseModel):
    query: str
    document_ids: list[str]


REQUIRED_AGENT_RESULT_KEYS = {"answer", "sources", "confidence"}


@router.post("/")
async def query_documents(payload: QueryRequest):

    try:
        if not payload.query or not payload.query.strip():
            raise ValueError("Query cannot be empty.")

        if not payload.document_ids:
            raise ValueError("At least one document_id is required.")

        result = agent_orchestrator.run(
            query=payload.query,
            document_ids=payload.document_ids,
        )

        if not isinstance(result, dict):
            raise AgentResponseError(
                f"Expected agent result to be dict, got {type(result).__name__}."
            )

        missing_keys = REQUIRED_AGENT_RESULT_KEYS - result.keys()
        if missing_keys:
            raise AgentResponseError(
                f"Agent response missing required fields: {', '.join(sorted(missing_keys))}."
            )

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
        }

    except HTTPException:
        raise

    except ValueError as e:
        logger.warning("Invalid query request: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except DocumentNotFoundError as e:
        logger.warning("Requested document was not found: %s", e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except AgentTimeoutError as e:
        logger.error("Agent timed out while processing query: %s", e)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The AI agent timed out while processing the request.",
        )

    except RetrievalError as e:
        logger.error("Document retrieval failed during query processing: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve relevant document context.",
        )

    except VectorStoreNotConfiguredError as e:
        logger.error("Vector store is not configured correctly: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector store is not properly configured.",
        )

    except VectorStoreError as e:
        logger.error("Vector store operation failed during query processing: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store operation failed.",
        )

    except LLMProviderError as e:
        logger.error("LLM provider failed during query processing: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider failed while generating the answer.",
        )

    except LLMResponseError as e:
        logger.error("LLM returned invalid or unusable response: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider returned an invalid response.",
        )

    except AgentResponseError as e:
        logger.error("Agent returned malformed response: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

    except AgentOrchestrationError as e:
        logger.error("Agent orchestration failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The AI agent failed while processing the request.",
        )

    except AppError as e:
        logger.error("Unhandled application error while querying documents: %s", e)
        raise to_http_exception(e)

    except Exception:
        logger.exception("🔥 UNEXPECTED BACKEND ERROR while querying documents 🔥")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected backend error while processing the query.",
        )