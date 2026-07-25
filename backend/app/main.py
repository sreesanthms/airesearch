"""
Main FastAPI application for ResearchPilot Backend.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.endpoints import upload as upload_endpoint
from app.api.v1.endpoints import retrieval as retrieval_endpoint
from app.api.v1.endpoints import chat as chat_endpoint
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan startup and shutdown events."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting up ResearchPilot Backend API")
    yield
    logger.info("Shutting down ResearchPilot Backend API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ResearchPilot Backend — PDF Text Extraction, FAISS RAG Indexing, and Gemini 2.5 Flash Q&A Engine",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API router under /api/v1
app.include_router(api_router, prefix="/api/v1")

# Also mount /upload, /retrieve, and /chat directly at root level to satisfy GET/POST requests directly
app.include_router(upload_endpoint.router, prefix="/upload", tags=["upload"])
app.include_router(retrieval_endpoint.router, prefix="/retrieve", tags=["retrieval"])
app.include_router(chat_endpoint.router, prefix="/chat", tags=["chat"])
