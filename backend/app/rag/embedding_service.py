"""
Singleton Embedding Service using Sentence Transformers with offline cache fallback.
"""
import time
import logging
import threading
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    """Singleton service for generating vector embeddings using SentenceTransformers."""

    _instance = None
    _lock = threading.Lock()
    _model = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingService, cls).__new__(cls)
                    cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        """Loads the SentenceTransformer model once during initialization with local cache fallback."""
        start_time = time.perf_counter()
        logger.info(f"Loading embedding model '{MODEL_NAME}'...")
        try:
            try:
                # Attempt offline load from local cache first to prevent network timeouts
                self._model = SentenceTransformer(MODEL_NAME, local_files_only=True)
                logger.info(f"Loaded '{MODEL_NAME}' from local HuggingFace cache.")
            except Exception:
                # Fall back to online fetch if model is not yet cached locally
                self._model = SentenceTransformer(MODEL_NAME)
                logger.info(f"Downloaded '{MODEL_NAME}' from HuggingFace Hub.")

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"Embedding model '{MODEL_NAME}' initialized in {elapsed_ms:.2f}ms.")
        except Exception as e:
            logger.error(f"Failed to load embedding model '{MODEL_NAME}': {str(e)}", exc_info=True)
            raise e

    def embed_text(self, text: str) -> np.ndarray:
        """Generates embedding vector for a single query text string.

        Args:
            text: Query string.

        Returns:
            2D numpy array of shape (1, embedding_dim) as float32.
        """
        if not text or not text.strip():
            raise ValueError("Query text cannot be empty.")

        start_time = time.perf_counter()
        embedding = self._model.encode([text], show_progress_bar=False, convert_to_numpy=True)
        embedding = np.array(embedding, dtype=np.float32)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Generated single embedding in {elapsed_ms:.2f}ms (Shape: {embedding.shape}).")
        return embedding

    def embed_chunks(self, texts: list[str]) -> np.ndarray:
        """Generates embedding vectors for a batch of text chunks.

        Args:
            texts: List of text chunk strings.

        Returns:
            2D numpy array of shape (num_chunks, embedding_dim) as float32.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        start_time = time.perf_counter()
        embeddings = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        embeddings = np.array(embeddings, dtype=np.float32)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Generated embeddings for {len(texts)} chunks in {elapsed_ms:.2f}ms "
            f"(Output shape: {embeddings.shape})."
        )
        return embeddings

    @property
    def embedding_dimension(self) -> int:
        """Returns the output vector dimension of the loaded embedding model."""
        if hasattr(self._model, "get_embedding_dimension"):
            return self._model.get_embedding_dimension()
        return self._model.get_sentence_embedding_dimension()
