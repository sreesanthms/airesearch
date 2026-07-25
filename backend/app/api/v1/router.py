"""
Main v1 API router.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, upload, retrieval, chat, summary

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(retrieval.router, prefix="/retrieve", tags=["retrieval"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(summary.router, prefix="/summary", tags=["summary"])
