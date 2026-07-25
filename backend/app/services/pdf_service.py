"""
PDF Service for handling PDF file persistence, text extraction, chunking, and FAISS indexing.
"""
import os
import time
import uuid
import logging
import fitz  # PyMuPDF
from pathlib import Path
from app.utils.text_cleaner import TextCleaner
from app.schemas.paper_schemas import PDFUploadResponse, PDFMetadata
from app.core.exceptions import PaperProcessingError
from app.rag.chunker import TextChunker
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


class PDFService:
    """Service class for saving PDF uploads, extracting text, chunking, and building FAISS indices."""

    def __init__(self, upload_dir: Path = UPLOAD_DIR):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.chunker = TextChunker(target_chunk_words=500, overlap_words=100)
        self.embedding_service = EmbeddingService()

    def _save_file(self, content: bytes, original_filename: str) -> Path:
        """Sanitizes filename and persists bytes using a unique UUID."""
        sanitized_basename = os.path.basename(original_filename)
        extension = Path(sanitized_basename).suffix or ".pdf"
        unique_name = f"{uuid.uuid4()}{extension}"
        file_path = self.upload_dir / unique_name

        while file_path.exists():
            unique_name = f"{uuid.uuid4()}{extension}"
            file_path = self.upload_dir / unique_name

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Saved uploaded PDF as '{unique_name}' (Original: '{sanitized_basename}')")
        return file_path

    def process_pdf(self, content: bytes, original_filename: str) -> PDFUploadResponse:
        """Extracts text page-by-page, generates embeddings, and saves FAISS vector index."""
        start_time = time.perf_counter()
        logger.info(f"Extraction & RAG indexing started for file: '{original_filename}'")

        # 1. Save PDF file
        file_path = self._save_file(content, original_filename)
        paper_id = file_path.name  # Use UUID filename as paper_id

        try:
            # 2. Extract page-by-page text with PyMuPDF context manager for safe handle cleanup
            page_records: list[tuple[int, str]] = []
            page_count = 0
            raw_metadata = {}

            with fitz.open(str(file_path)) as doc:
                page_count = doc.page_count
                raw_metadata = doc.metadata or {}

                for page_num in range(page_count):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text:
                        cleaned_page_text = TextCleaner.clean_text(page_text)
                        page_records.append((page_num + 1, cleaned_page_text))

            full_raw_text = "\n\n".join([text for _, text in page_records])
            cleaned_text = TextCleaner.clean_text(full_raw_text)

            word_count = len(cleaned_text.split())
            character_count = len(cleaned_text)

            # 3. Extract and sanitize PDF metadata
            def sanitize_meta(value: str | None) -> str | None:
                if not value or not str(value).strip():
                    return None
                return str(value).strip()

            pdf_metadata = PDFMetadata(
                title=sanitize_meta(raw_metadata.get("title")),
                author=sanitize_meta(raw_metadata.get("author")),
                subject=sanitize_meta(raw_metadata.get("subject")),
                creator=sanitize_meta(raw_metadata.get("creator")),
                producer=sanitize_meta(raw_metadata.get("producer")),
            )

            preview = cleaned_text[:1000]

            # 4. Generate paragraph-aware chunks
            chunk_start = time.perf_counter()
            chunks = self.chunker.chunk_page_pages(page_records)
            chunk_time_ms = (time.perf_counter() - chunk_start) * 1000

            # 5. Generate embeddings for chunks
            embed_start = time.perf_counter()
            chunk_texts = [c["text"] for c in chunks]
            embeddings = self.embedding_service.embed_chunks(chunk_texts)
            embed_time_ms = (time.perf_counter() - embed_start) * 1000

            # 6. Build and save FAISS index + metadata
            index_start = time.perf_counter()
            vector_store = VectorStore()
            vector_store.create_index(self.embedding_service.embedding_dimension)
            vector_store.add_documents(embeddings, chunks)
            vector_store.save_index(paper_id)
            index_time_ms = (time.perf_counter() - index_start) * 1000

            total_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"PDF Processing & RAG indexing finished for '{paper_id}' in {total_ms:.2f}ms "
                f"(Chunking: {chunk_time_ms:.2f}ms, Embedding: {embed_time_ms:.2f}ms, FAISS Indexing: {index_time_ms:.2f}ms). "
                f"Total Chunks: {len(chunks)}"
            )

            return PDFUploadResponse(
                success=True,
                file_name=paper_id,
                pages=page_count,
                word_count=word_count,
                character_count=character_count,
                metadata=pdf_metadata,
                preview=preview,
            )

        except Exception as e:
            logger.error(f"Error during PDF processing for '{original_filename}': {str(e)}", exc_info=True)
            raise PaperProcessingError(f"Failed to extract text and index PDF document: {str(e)}")
