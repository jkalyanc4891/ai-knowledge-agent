import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api import api_router
from app.vectorstore.base import VectorStore
from app.validation.guardrails import SafetyEngine


def create_app() -> FastAPI:
    """
    Application factory for FastAPI.
    Ensures clean initialization of:
    - logging
    - vector store
    - safety engine
    - routers
    """

    # -------------------------
    # Logging
    # -------------------------
    setup_logging()
    logger.info("Starting AI Knowledge & Decision Support System")

    # -------------------------
    # FastAPI App
    # -------------------------
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Enterprise RAG + Agentic AI System with Safety Guardrails",
    )

    # -------------------------
    # CORS (UI → API)
    # -------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------
    # Vector Store Initialization
    # -------------------------
    logger.info(f"Initializing vector store backend: {settings.VECTOR_DB_BACKEND}")
    app.state.vector_store = VectorStore.get_store(settings.VECTOR_DB_BACKEND)

    # -------------------------
    # Safety Engine Initialization
    # -------------------------
    app.state.safety_engine = SafetyEngine()

    # -------------------------
    # API Router
    # -------------------------
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()


# -------------------------
# Local Development Server
# -------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )