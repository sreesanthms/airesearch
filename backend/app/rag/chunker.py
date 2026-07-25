"""
Text Chunking module for page-aware, paragraph-preserving document chunking.
"""
import uuid
import logging
import re
from typing import TypedDict

logger = logging.getLogger(__name__)


class ChunkMetadata(TypedDict):
    """TypedDict structure for chunk metadata."""

    id: str
    page: int
    text: str
    word_count: int


class TextChunker:
    """Paragraph-aware text chunker with page tracking, word limit enforcement, and overlap."""

    def __init__(self, target_chunk_words: int = 500, overlap_words: int = 100):
        """Initializes TextChunker.

        Args:
            target_chunk_words: Target word count per chunk (default: 500).
            overlap_words: Overlap word count between consecutive chunks (default: 100).
        """
        self.target_chunk_words = target_chunk_words
        self.overlap_words = overlap_words

    def _split_into_paragraphs(self, text: str) -> list[str]:
        """Splits text into paragraphs by double newlines or structural line breaks."""
        if not text:
            return []
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        return paragraphs if paragraphs else [text.strip()]

    def chunk_page_pages(self, page_records: list[tuple[int, str]]) -> list[ChunkMetadata]:
        """Chunks a document given a list of (page_number, page_text) tuples.

        Args:
            page_records: List of tuples containing (1-indexed page_number, page_text).

        Returns:
            List of ChunkMetadata dictionaries.
        """
        chunks: list[ChunkMetadata] = []

        for page_num, page_text in page_records:
            if not page_text or not page_text.strip():
                continue

            paragraphs = self._split_into_paragraphs(page_text)
            current_words: list[str] = []
            current_para_buffer: list[str] = []

            for para in paragraphs:
                para_words = para.split()
                if not para_words:
                    continue

                # If single paragraph exceeds target chunk size, split it directly by words
                if len(para_words) > self.target_chunk_words:
                    # Flush any accumulated buffer first
                    if current_para_buffer:
                        chunk_text = "\n\n".join(current_para_buffer)
                        chunks.append(
                            {
                                "id": str(uuid.uuid4()),
                                "page": page_num,
                                "text": chunk_text,
                                "word_count": len(chunk_text.split()),
                            }
                        )
                        current_para_buffer = []
                        current_words = []

                    # Chunk oversized paragraph in word slices
                    for i in range(0, len(para_words), self.target_chunk_words - self.overlap_words):
                        slice_words = para_words[i : i + self.target_chunk_words]
                        slice_text = " ".join(slice_words)
                        chunks.append(
                            {
                                "id": str(uuid.uuid4()),
                                "page": page_num,
                                "text": slice_text,
                                "word_count": len(slice_words),
                            }
                        )
                    continue

                # Check if adding paragraph exceeds target chunk size
                if len(current_words) + len(para_words) > self.target_chunk_words and current_para_buffer:
                    # Emit current chunk
                    chunk_text = "\n\n".join(current_para_buffer)
                    chunks.append(
                        {
                            "id": str(uuid.uuid4()),
                            "page": page_num,
                            "text": chunk_text,
                            "word_count": len(current_words),
                        }
                    )

                    # Compute overlap from end of current_words
                    overlap_tail_words = current_words[-self.overlap_words :] if len(current_words) >= self.overlap_words else current_words
                    overlap_prefix = " ".join(overlap_tail_words)

                    # Reset buffer starting with overlap text + new paragraph
                    current_para_buffer = [overlap_prefix, para] if overlap_prefix else [para]
                    current_words = overlap_tail_words + para_words
                else:
                    current_para_buffer.append(para)
                    current_words.extend(para_words)

            # Flush remaining buffer for the page
            if current_para_buffer:
                chunk_text = "\n\n".join(current_para_buffer)
                chunks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "page": page_num,
                        "text": chunk_text,
                        "word_count": len(current_words),
                    }
                )

        logger.info(f"Chunking complete. Created {len(chunks)} chunks from {len(page_records)} pages.")
        return chunks
