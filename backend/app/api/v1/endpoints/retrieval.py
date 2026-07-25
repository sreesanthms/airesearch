"""
Retrieval API endpoint module for RAG search.
"""
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from app.rag.retriever import Retriever
from app.schemas.paper_schemas import RetrievalRequest, RetrievalResponse, RetrievalResultItem
from app.core.exceptions import PaperNotFoundError, PaperProcessingError
from app.rag.vector_store import FAISS_STORAGE_DIR

logger = logging.getLogger(__name__)
router = APIRouter()
retriever_service = Retriever()


def _get_latest_paper_id() -> str | None:
    """Helper to find the most recently updated FAISS index in storage/faiss/."""
    if not FAISS_STORAGE_DIR.exists():
        return None

    indices = list(FAISS_STORAGE_DIR.glob("*.index"))
    if not indices:
        return None

    # Sort by last modification time descending
    indices.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest_path = indices[0]
    return latest_path.stem  # e.g., 'uuid-filename.pdf'


@router.post(
    "",
    response_model=RetrievalResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve top relevant paper chunks for query",
    description="Embeds user query, performs FAISS vector search, and returns top 5 relevant document passages sorted by similarity score.",
)
async def retrieve_chunks(request: RetrievalRequest) -> RetrievalResponse:
    """Endpoint for RAG text chunk retrieval.

    Args:
        request: RetrievalRequest object containing query string and optional paper_id.

    Returns:
        RetrievalResponse object containing top matching chunk passages.
    """
    query = request.query.strip() if request.query else ""
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty.",
        )

    paper_id = request.paper_id
    if not paper_id:
        paper_id = _get_latest_paper_id()
        if not paper_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No indexed paper found. Please upload a PDF paper first before searching.",
            )
        logger.info(f"paper_id omitted. Defaulting to latest indexed paper: '{paper_id}'")

    try:
        results = retriever_service.retrieve(
            query=query,
            paper_id=paper_id,
            top_k=request.top_k,
        )

        formatted_results = [
            RetrievalResultItem(
                page=r["page"],
                score=r["score"],
                text=r["text"],
            )
            for r in results
        ]

        return RetrievalResponse(
            query=query,
            results=formatted_results,
        )

    except PaperNotFoundError as e:
        logger.warning(f"Retrieval failed - Paper index not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Internal server error during RAG retrieval: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during vector retrieval: {str(e)}",
        )
