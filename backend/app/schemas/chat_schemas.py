"""
Pydantic schemas for chat requests, streaming responses, and conversation memory.
"""
from pydantic import BaseModel, Field


class MessageItem(BaseModel):
    """Single message item in conversation memory."""

    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    """Request model for POST /chat streaming endpoint."""

    paper_id: str | None = Field(None, description="Paper UUID/filename. If omitted, uses latest uploaded paper.")
    question: str = Field(..., description="User question about the paper", min_length=1)
    history: list[MessageItem] = Field(default=[], description="Recent conversation history (max 5 Q&A pairs used)")


class ChatStreamChunk(BaseModel):
    """SSE streamed token event or final done indicator."""

    token: str | None = None
    done: bool = False
    error: str | None = None
