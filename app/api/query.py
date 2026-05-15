from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.pipeline import RAGPipeline
from app.agents.orchestrator import AgentOrchestrator
from app.vectorstore.base import VectorStore
from app.core.config import settings
import logging, traceback

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

vector_store = VectorStore.get_store(settings.VECTOR_DB_BACKEND)
rag_pipeline = RAGPipeline(vector_store)
agent_orchestrator = AgentOrchestrator(rag_pipeline, vector_store)


class QueryRequest(BaseModel):
    query: str
    document_ids: list[str]


@router.post("/")
async def query_documents(payload: QueryRequest):
    """
    Runs the full agentic RAG pipeline:
    - Planner agent decides retrieval strategy
    - Retriever fetches relevant chunks
    - RAG pipeline synthesizes answer
    - Validator agent checks grounding
    """

    try:
        result = agent_orchestrator.run(
            query=payload.query,
            document_ids=payload.document_ids
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"]
        }

    except Exception as e:
        logger.error("🔥 BACKEND ERROR 🔥\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))