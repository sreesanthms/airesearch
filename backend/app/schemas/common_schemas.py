"""
Common schemas.
"""
from pydantic import BaseModel

class HealthResponse(BaseModel):
    """Response for health check."""
    status: str
    version: str

class ErrorResponse(BaseModel):
    """Response for errors."""
    detail: str
