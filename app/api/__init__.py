from fastapi import APIRouter
from .documents import  router as documents_router
from .query import router as query_router
from .health import router as health_router

api_router = APIRouter()

api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(query_router, prefix="/query", tags=["Query"])
api_router.include_router(health_router, prefix="/health", tags=["Health"])