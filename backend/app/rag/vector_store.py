"""
FAISS Vector Store module with metadata persistence and path sanitization.
"""
import os
import json
import time
import logging
import numpy as np
import faiss
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory for FAISS indices and JSON metadata
FAISS_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "faiss"


class VectorStore:
    """FAISS Vector Store manager for IndexFlatL2 with parallel JSON metadata storage."""

    def __init__(self, storage_dir: Path = FAISS_STORAGE_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index: faiss.IndexFlatL2 | None = None
        self.metadata_store: list[dict] = []
        self.dimension: int = 384  # Default dimension for all-MiniLM-L6-v2

    @staticmethod
    def _sanitize_paper_id(paper_id: str) -> str:
        """Sanitizes paper_id to prevent directory traversal attacks."""
        clean_id = os.path.basename(paper_id.strip())
        if not clean_id:
            raise ValueError("Invalid or empty paper_id.")
        return clean_id

    def create_index(self, dimension: int = 384) -> None:
        """Initializes a new empty FAISS IndexFlatL2 index.

        Args:
            dimension: Embedding vector dimension.
        """
        start_time = time.perf_counter()
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata_store = []
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Created new FAISS IndexFlatL2 (dim={dimension}) in {elapsed_ms:.2f}ms.")

    def add_documents(self, embeddings: np.ndarray, metadata: list[dict]) -> None:
        """Adds embedding vectors and parallel metadata dicts to the index.

        Args:
            embeddings: 2D numpy array of shape (num_vectors, dimension) float32.
            metadata: List of chunk metadata dicts matching the vector count.
        """
        if self.index is None:
            self.create_index(embeddings.shape[1] if embeddings.ndim == 2 else self.dimension)

        if embeddings.size == 0 or not metadata:
            logger.warning("No embeddings or metadata provided to add_documents.")
            return

        if len(embeddings) != len(metadata):
            raise ValueError(f"Embeddings count ({len(embeddings)}) does not match metadata count ({len(metadata)}).")

        start_time = time.perf_counter()
        # FAISS requires C-contiguous float32 array
        vectors = np.ascontiguousarray(embeddings, dtype=np.float32)
        self.index.add(vectors)
        self.metadata_store.extend(metadata)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Added {len(metadata)} vectors to FAISS index in {elapsed_ms:.2f}ms (Total index size: {self.index.ntotal}).")

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[dict]:
        """Searches the index for top_k nearest neighbors given a query embedding.

        Args:
            query_vector: 2D numpy array of shape (1, dimension) float32.
            top_k: Number of nearest neighbors to retrieve.

        Returns:
            List of metadata dicts with added 'l2_distance' and 'score' (normalized similarity).
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Search called on empty or uninitialized FAISS index.")
            return []

        start_time = time.perf_counter()
        q_vec = np.ascontiguousarray(query_vector, dtype=np.float32)
        
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(q_vec, k)

        results: list[dict] = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.metadata_store):
                continue

            dist = float(distances[0][i])
            # Convert L2 distance to normalized similarity score [0.0, 1.0]
            similarity_score = 1.0 / (1.0 + dist)

            meta = dict(self.metadata_store[idx])
            meta["l2_distance"] = round(dist, 4)
            meta["score"] = round(similarity_score, 4)
            results.append(meta)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"FAISS search executed in {elapsed_ms:.2f}ms. Returned {len(results)} results.")
        return results

    def save_index(self, paper_id: str) -> None:
        """Saves FAISS index to disk as '{paper_id}.index' and metadata as '{paper_id}_metadata.json'.

        Args:
            paper_id: Unique paper identifier.
        """
        if self.index is None:
            raise ValueError("Cannot save index: FAISS index is not initialized.")

        clean_id = self._sanitize_paper_id(paper_id)
        start_time = time.perf_counter()
        index_path = self.storage_dir / f"{clean_id}.index"
        meta_path = self.storage_dir / f"{clean_id}_metadata.json"

        faiss.write_index(self.index, str(index_path))
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata_store, f, indent=2, ensure_ascii=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Saved FAISS index and metadata for paper_id='{clean_id}' to '{self.storage_dir}' in {elapsed_ms:.2f}ms.")

    def load_index(self, paper_id: str) -> bool:
        """Loads FAISS index and metadata from disk securely.

        Args:
            paper_id: Unique paper identifier.

        Returns:
            True if loaded successfully, False if index files do not exist.
        """
        clean_id = self._sanitize_paper_id(paper_id)
        index_path = self.storage_dir / f"{clean_id}.index"
        meta_path = self.storage_dir / f"{clean_id}_metadata.json"

        if not index_path.exists() or not meta_path.exists():
            logger.warning(f"FAISS index files for paper_id='{clean_id}' not found at '{self.storage_dir}'.")
            return False

        start_time = time.perf_counter()
        self.index = faiss.read_index(str(index_path))
        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata_store = json.load(f)

        self.dimension = self.index.d
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Loaded FAISS index and {len(self.metadata_store)} metadata items for paper_id='{clean_id}' in {elapsed_ms:.2f}ms."
        )
        return True
