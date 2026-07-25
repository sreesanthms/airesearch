"""
Pydantic schemas for paper upload, extraction, and RAG retrieval responses.
"""
from pydantic import BaseModel, Field


class PDFMetadata(BaseModel):
    """PDF Document Metadata Schema."""

    title: str | None = None
    author: str | None = None
    subject: str | None = None
    creator: str | None = None
    producer: str | None = None


class PDFUploadResponse(BaseModel):
    """Response model for PDF upload, text extraction, and FAISS indexing."""

    success: bool = True
    file_name: str = Field(..., description="Unique filename assigned in uploads directory (paper_id)")
    pages: int = Field(..., description="Total page count")
    word_count: int = Field(..., description="Total word count in cleaned text")
    character_count: int = Field(..., description="Total character count in cleaned text")
    metadata: PDFMetadata = Field(..., description="PDF document metadata attributes")
    preview: str = Field(..., description="First 1000 characters preview of extracted text")


class RetrievalRequest(BaseModel):
    """Request model for /retrieve endpoint."""

    paper_id: str | None = Field(None, description="Unique paper filename/ID. If omitted, uses latest index.")
    query: str = Field(..., description="Natural language search query string", min_length=1)
    top_k: int = Field(5, description="Number of top relevant chunks to retrieve", ge=1, le=20)


class RetrievalResultItem(BaseModel):
    """Individual chunk retrieval result item."""

    page: int = Field(..., description="1-indexed page number where chunk appears")
    score: float = Field(..., description="Normalized cosine/L2 similarity score [0.0 to 1.0]")
    text: str = Field(..., description="Extracted text chunk content")


class RetrievalResponse(BaseModel):
    """Response model for /retrieve endpoint."""

    query: str = Field(..., description="Original query string")
    results: list[RetrievalResultItem] = Field(..., description="Top relevant retrieved chunks sorted by score")
