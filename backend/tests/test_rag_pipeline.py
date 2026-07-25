"""
Comprehensive test suite for the RAG pipeline (Embedding, Chunking, VectorStore, Retriever, /retrieve API).
"""
import io
import fitz
import numpy as np
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.rag.embedding_service import EmbeddingService
from app.rag.chunker import TextChunker
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever

client = TestClient(app)


def create_sample_pdf(text: str) -> bytes:
    """Helper to generate in-memory PDF using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_embedding_service_singleton():
    """Verify EmbeddingService implements Singleton pattern."""
    srv1 = EmbeddingService()
    srv2 = EmbeddingService()
    assert srv1 is srv2

    vec = srv1.embed_text("What is the methodology?")
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (1, 384)


def test_text_chunker():
    """Verify TextChunker preserves page numbers and chunk constraints."""
    chunker = TextChunker(target_chunk_words=50, overlap_words=10)
    page_records = [(1, "Word " * 120), (2, "Second page text content " * 10)]
    chunks = chunker.chunk_page_pages(page_records)

    assert len(chunks) > 0
    for chunk in chunks:
        assert "id" in chunk
        assert "page" in chunk
        assert "text" in chunk
        assert "word_count" in chunk
        assert chunk["page"] in (1, 2)


def test_vector_store_persistence(tmp_path):
    """Verify VectorStore creates, searches, saves, and loads FAISS IndexFlatL2."""
    vs = VectorStore(storage_dir=tmp_path)
    vs.create_index(dimension=384)

    embeddings = np.random.rand(3, 384).astype(np.float32)
    metadata = [
        {"id": "c1", "page": 1, "text": "First chunk text", "word_count": 3},
        {"id": "c2", "page": 2, "text": "Second chunk text", "word_count": 3},
        {"id": "c3", "page": 3, "text": "Third chunk text", "word_count": 3},
    ]

    vs.add_documents(embeddings, metadata)
    assert vs.index.ntotal == 3

    vs.save_index("test_paper")
    assert (tmp_path / "test_paper.index").exists()
    assert (tmp_path / "test_paper_metadata.json").exists()

    vs_loaded = VectorStore(storage_dir=tmp_path)
    loaded = vs_loaded.load_index("test_paper")
    assert loaded is True
    assert vs_loaded.index.ntotal == 3
    assert len(vs_loaded.metadata_store) == 3


def test_end_to_end_upload_and_retrieve_api():
    """Test full workflow: upload PDF -> auto-index in FAISS -> query via POST /retrieve."""
    sample_text = (
        "Methodology Section:\n"
        "We propose a novel Transformer architecture utilizing self-attention mechanisms. "
        "The encoder consists of 6 stacked layers with multi-head attention. "
        "The model is evaluated on WMT 2014 English-to-German translation tasks."
    )
    pdf_bytes = create_sample_pdf(sample_text)

    # 1. Upload PDF
    upload_res = client.post(
        "/upload",
        files={"file": ("transformer_paper.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    paper_id = upload_data["file_name"]

    # 2. Retrieve top chunks via /retrieve API
    retrieve_res = client.post(
        "/retrieve",
        json={"paper_id": paper_id, "query": "What methodology and architecture is used?", "top_k": 5},
    )
    assert retrieve_res.status_code == 200
    retrieve_data = retrieve_res.json()

    assert retrieve_data["query"] == "What methodology and architecture is used?"
    assert "results" in retrieve_data
    assert len(retrieve_data["results"]) > 0

    first_result = retrieve_data["results"][0]
    assert "page" in first_result
    assert "score" in first_result
    assert "text" in first_result
    assert first_result["page"] == 1
    assert first_result["score"] > 0.0
    assert "Transformer" in first_result["text"]


def test_retrieve_missing_index_error():
    """Test POST /retrieve returns 404 for non-existent paper index."""
    res = client.post(
        "/retrieve",
        json={"paper_id": "non_existent_paper_xyz.pdf", "query": "Test query"},
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_retrieve_empty_query_error():
    """Test POST /retrieve returns 400 for empty query string."""
    res = client.post(
        "/retrieve",
        json={"paper_id": "some_id", "query": "   "},
    )
    assert res.status_code == 400
    assert "cannot be empty" in res.json()["detail"].lower()
