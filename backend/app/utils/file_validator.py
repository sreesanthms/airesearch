"""
Utility module for validating PDF uploads.
"""
import fitz  # PyMuPDF
from fastapi import UploadFile
from app.core.exceptions import FileValidationError

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class FileValidator:
    """Validator class for verifying PDF file integrity, size, and extractable content."""

    @staticmethod
    async def validate_pdf_upload(file: UploadFile) -> bytes:
        """Validates an uploaded file to ensure it is a valid, unencrypted, text-containing PDF.

        Args:
            file: FastAPI UploadFile object.

        Returns:
            The raw bytes of the validated PDF file.

        Raises:
            FileValidationError: If any validation check fails.
        """
        # 1. Check filename extension
        filename = file.filename or ""
        if not filename.lower().endswith(".pdf"):
            raise FileValidationError("Only PDF files are allowed. Invalid file extension.")

        # 2. Read file content and check size limit
        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise FileValidationError("Uploaded PDF file is empty (0 bytes).")

        if file_size > MAX_FILE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            raise FileValidationError(
                f"File size exceeds the maximum limit of 25MB (Uploaded: {size_mb:.2f}MB)."
            )

        # 3. Check PDF magic bytes (%PDF-)
        if not content.startswith(b"%PDF-"):
            raise FileValidationError("Invalid file format. Magic bytes signature does not match PDF.")

        # 4. Open PDF with PyMuPDF context manager to inspect structure and content safely
        try:
            with fitz.open(stream=content, filetype="pdf") as doc:
                # 5. Check if PDF is encrypted
                if doc.is_encrypted:
                    raise FileValidationError("Encrypted or password-protected PDF files are not supported.")

                # 6. Check page count
                if doc.page_count == 0:
                    raise FileValidationError("PDF document contains no pages.")

                # 7. Check if PDF is a scanned image-only document with zero extractable text
                total_text_length = sum(len(page.get_text().strip()) for page in doc)

                if total_text_length == 0:
                    raise FileValidationError(
                        "Scanned image-only PDF with no selectable text. OCR is required for this file."
                    )
        except FileValidationError:
            raise
        except Exception as e:
            raise FileValidationError(f"Corrupted or invalid PDF file: {str(e)}")

        return content
