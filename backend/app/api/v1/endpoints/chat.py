"""
Chat API endpoint module providing Server-Sent Events (SSE) streaming answers via RAG + Gemini.
"""
import json
import logging
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.rag.retriever import Retriever
from app.llm.prompt_builder import PromptBuilder
from app.llm.gemini_service import GeminiService
from app.schemas.chat_schemas import ChatRequest
from app.core.exceptions import PaperNotFoundError
from app.rag.vector_store import FAISS_STORAGE_DIR
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

retriever = Retriever()
gemini_service = GeminiService()


def _get_latest_paper_id() -> str | None:
    """Helper to find the most recently updated FAISS index in storage/faiss/."""
    if not FAISS_STORAGE_DIR.exists():
        return None
    indices = list(FAISS_STORAGE_DIR.glob("*.index"))
    if not indices:
        return None
    indices.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return indices[0].stem


async def _stream_rag_passages(question: str, retrieved_chunks: list[dict], note_suffix: str) -> AsyncGenerator[str, None]:
    """Helper to stream retrieved RAG passages smoothly via SSE events."""
    intro = f"**Top Relevant Passages** retrieved from paper for *\"{question}\"*:\n\n"
    yield f"data: {json.dumps({'token': intro})}\n\n"
    await asyncio.sleep(0.01)

    for i, chunk in enumerate(retrieved_chunks, 1):
        page_num = chunk.get("page", 1)
        score = chunk.get("score", 0.0)
        text_snippet = chunk.get("text", "").strip()
        score_pct = int(score * 100)

        header = f"### Passage {i} — [Page {page_num}] (Match: {score_pct}%)\n"
        yield f"data: {json.dumps({'token': header})}\n\n"
        await asyncio.sleep(0.01)

        # Stream passage text in word chunks for fluid animation
        words = text_snippet.split(" ")
        chunk_buf = []
        for w in words:
            chunk_buf.append(w)
            if len(chunk_buf) >= 4:
                yield f"data: {json.dumps({'token': ' '.join(chunk_buf) + ' '})}\n\n"
                chunk_buf = []
                await asyncio.sleep(0.01)
        if chunk_buf:
            yield f"data: {json.dumps({'token': ' '.join(chunk_buf) + '\n\n'})}\n\n"

    if note_suffix:
        note_text = f"\n---\n> {note_suffix}"
        yield f"data: {json.dumps({'token': note_text})}\n\n"


@router.post(
    "",
    summary="Chat with research paper using RAG and Gemini (SSE Streaming)",
    description="Retrieves relevant document passages, constructs a prompt, and streams response tokens via Server Sent Events.",
)
async def chat_with_paper(request: ChatRequest) -> StreamingResponse:
    """Endpoint for streaming RAG Q&A answers via SSE."""
    question = request.question.strip() if request.question else ""
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    paper_id = request.paper_id
    if not paper_id:
        paper_id = _get_latest_paper_id()
        if not paper_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No indexed paper found. Please upload a PDF paper first before starting chat.",
            )

    # 1. Retrieve top 5 relevant document chunks
    retrieved_chunks = []
    try:
        retrieved_chunks = retriever.retrieve(query=question, paper_id=paper_id, top_k=5)
    except PaperNotFoundError as e:
        logger.warning(f"Chat request failed - Paper index missing: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Retrieval error during chat request: {str(e)}", exc_info=True)

    # 2. Build prompt with system constraints & token trimming
    prompt = PromptBuilder.build_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
        history=request.history,
    )

    # 3. Create Server-Sent Events (SSE) stream generator
    async def sse_event_generator() -> AsyncGenerator[str, None]:
        if not retrieved_chunks:
            fallback_msg = "I couldn't find that information in the uploaded paper."
            yield f"data: {json.dumps({'token': fallback_msg})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
            return

        current_settings = get_settings()
        api_key = current_settings.gemini_api_key.strip() if current_settings.gemini_api_key else ""

        # If API key is unconfigured, stream RAG context directly
        if not api_key or api_key == "your-gemini-api-key-here":
            async for sse_chunk in _stream_rag_passages(
                question,
                retrieved_chunks,
                "💡 *Note*: Add a valid `GEMINI_API_KEY` in `backend/.env` to enable full AI synthesis.",
            ):
                yield sse_chunk
            yield f"data: {json.dumps({'done': True})}\n\n"
            return

        # Attempt Gemini API streaming
        stream_tokens_sent = 0
        error_occurred = False

        try:
            async for token in gemini_service.generate_stream(prompt):
                if token:
                    if "Could not connect to Gemini API models" in token or "GEMINI_API_KEY is not configured" in token:
                        error_occurred = True
                        break
                    stream_tokens_sent += 1
                    yield f"data: {json.dumps({'token': token})}\n\n"

            if error_occurred or stream_tokens_sent == 0:
                logger.warning("Gemini stream returned error or quota limit. Streaming RAG passages directly...")
                async for sse_chunk in _stream_rag_passages(
                    question,
                    retrieved_chunks,
                    "⚠️ *Note*: Gemini API quota limit reached. Showing retrieved paper passages directly above.",
                ):
                    yield sse_chunk

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Error in SSE stream generator: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
