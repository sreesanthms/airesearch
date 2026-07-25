"""
RAG Context Retriever module.
"""
import time
import logging
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore
from app.core.exceptions import PaperNotFoundError, PaperProcessingError

logger = logging.getLogger(__name__)


class Retriever:
    """Orchestrates query embedding, vector store retrieval, and score sorting."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def retrieve(self, query: str, paper_id: str, top_k: int = 5) -> list[dict]:
        """Retrieves top_k relevant chunk passages for a query from a specific paper index.

        Args:
            query: Natural language query string.
            paper_id: Unique identifier for the paper/FAISS index.
            top_k: Number of relevant chunks to retrieve (default: 5).

        Returns:
            List of result dicts sorted by similarity score descending:
            [
                {
                    "page": 7,
                    "score": 0.92,
                    "text": "..."
                }
            ]

        Raises:
            ValueError: If query is empty.
            PaperNotFoundError: If FAISS index for paper_id does not exist.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        start_time = time.perf_counter()
        logger.info(f"Retrieval started for paper_id='{paper_id}', query='{query[:50]}...'")

        # 1. Load paper index and metadata from disk if not already loaded
        loaded = self.vector_store.load_index(paper_id)
        if not loaded:
            raise PaperNotFoundError(
                f"Vector index for paper_id='{paper_id}' not found. Please upload and index the PDF paper first."
            )

        # 2. Embed the query
        query_vector = self.embedding_service.embed_text(query.strip())

        # 3. Search FAISS index
        raw_results = self.vector_store.search(query_vector, top_k=top_k)

        # 4. Format and sort by similarity score descending
        formatted_results = []
        for item in raw_results:
            formatted_results.append(
                {
                    "page": item.get("page", 1),
                    "score": item.get("score", 0.0),
                    "text": item.get("text", ""),
                }
            )

        # Ensure sorted by score descending
        formatted_results.sort(key=lambda x: x["score"], reverse=True)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Retrieval finished for paper_id='{paper_id}' in {elapsed_ms:.2f}ms. "
            f"Returned {len(formatted_results)} sorted chunks."
        )

        return formatted_results
