"""
Unit and integration tests for PDF upload and extraction logic.
"""
import io
import fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.text_cleaner import TextCleaner
from app.utils.file_validator import FileValidator
from app.core.exceptions import FileValidationError

client = TestClient(app)


def create_sample_pdf(text: str = "Sample Research Paper Text Content") -> bytes:
    """Helper to create an in-memory PDF with specified text using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_text_cleaner():
    """Test text cleaning and paragraph preservation."""
    raw = "Line 1  \r\n\r\n\r\nLine 2\twith   extra spaces\n\n\nLine 3"
    cleaned = TextCleaner.clean_text(raw)
    assert "Line 1" in cleaned
    assert "Line 2 with extra spaces" in cleaned
    assert "\n\n" in cleaned
    assert "\n\n\n" not in cleaned


def test_valid_pdf_upload():
    """Test uploading a valid PDF document."""
    pdf_content = create_sample_pdf("Abstract: This paper presents a novel RAG evaluation benchmark.")
    
    response = client.post(
        "/upload",
        files={"file": ("test_paper.pdf", pdf_content, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "file_name" in data
    assert data["pages"] == 1
    assert data["word_count"] > 0
    assert data["character_count"] > 0
    assert "Abstract:" in data["preview"]
    assert "metadata" in data


def test_non_pdf_upload_rejected():
    """Test that non-PDF files are rejected with 415 or 422 error."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"Hello world text file", "text/plain")},
    )
    assert response.status_code in (415, 422)


def test_empty_pdf_rejected():
    """Test that 0-byte or empty PDFs are rejected."""
    response = client.post(
        "/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code in (400, 422)


def test_scanned_image_only_pdf_rejected():
    """Test that PDFs without text content are rejected."""
    # Create empty PDF page with no text
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.write()
    doc.close()

    response = client.post(
        "/upload",
        files={"file": ("scanned.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 422
    assert "Scanned image-only PDF" in response.json()["detail"]
