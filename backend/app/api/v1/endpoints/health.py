"""
Health check endpoints.
"""
from fastapi import APIRouter
from app.schemas.common_schemas import HealthResponse

router = APIRouter()

@router.get("/", response_model=dict)
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to ResearchPilot API", "version": "1.0.0"}

@router.get("/health", response_model=HealthResponse)
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
