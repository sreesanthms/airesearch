"""
Preset paper analysis endpoints: /summary, /methodology, /viva, and /future-work.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.rag.retriever import Retriever
from app.core.exceptions import PaperNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter()
retriever = Retriever()


class PresetAnalysisRequest(BaseModel):
    """Request model for preset paper analysis endpoints."""

    paper_id: str = Field(..., description="Unique paper filename/ID")


class PresetAnalysisResponse(BaseModel):
    """Response model for preset paper analysis endpoints."""

    success: bool = True
    paper_id: str
    preset_type: str
    passages: list[dict]


@router.post("/summary", response_model=PresetAnalysisResponse, summary="Get paper summary passages")
async def summarize_paper(request: PresetAnalysisRequest) -> PresetAnalysisResponse:
    """Retrieves key paper summary passages from RAG index."""
    try:
        results = retriever.retrieve("Provide a comprehensive executive summary of this paper.", request.paper_id, top_k=5)
        return PresetAnalysisResponse(success=True, paper_id=request.paper_id, preset_type="summary", passages=results)
    except PaperNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/methodology", response_model=PresetAnalysisResponse, summary="Get methodology breakdown passages")
async def analyze_methodology(request: PresetAnalysisRequest) -> PresetAnalysisResponse:
    """Retrieves methodology and technical architecture passages from RAG index."""
    try:
        results = retriever.retrieve("Explain the core methodology, architecture, and mathematical formulation.", request.paper_id, top_k=5)
        return PresetAnalysisResponse(success=True, paper_id=request.paper_id, preset_type="methodology", passages=results)
    except PaperNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/viva", response_model=PresetAnalysisResponse, summary="Get viva examination question passages")
async def generate_viva(request: PresetAnalysisRequest) -> PresetAnalysisResponse:
    """Retrieves core concepts for viva exam questions from RAG index."""
    try:
        results = retriever.retrieve("Identify key novel contributions and potential viva examination questions.", request.paper_id, top_k=5)
        return PresetAnalysisResponse(success=True, paper_id=request.paper_id, preset_type="viva", passages=results)
    except PaperNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/future-work", response_model=PresetAnalysisResponse, summary="Get future work and limitations passages")
async def analyze_future_work(request: PresetAnalysisRequest) -> PresetAnalysisResponse:
    """Retrieves future research directions and paper limitations from RAG index."""
    try:
        results = retriever.retrieve("Summarize limitations and proposed future research directions.", request.paper_id, top_k=5)
        return PresetAnalysisResponse(success=True, paper_id=request.paper_id, preset_type="future-work", passages=results)
    except PaperNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
