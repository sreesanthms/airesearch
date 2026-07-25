"""
Endpoint module for handling PDF file uploads and text extraction.
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.utils.file_validator import FileValidator
from app.services.pdf_service import PDFService
from app.schemas.paper_schemas import PDFUploadResponse
from app.core.exceptions import FileValidationError, PaperProcessingError

logger = logging.getLogger(__name__)
router = APIRouter()
pdf_service = PDFService()


@router.post(
    "",
    response_model=PDFUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload PDF and extract text",
    description="Accepts a PDF document via multipart form upload, validates structure, saves with a UUID filename, and returns extracted text metadata, page count, word count, and 1000-char preview.",
)
async def upload_pdf(file: UploadFile = File(...)) -> PDFUploadResponse:
    """Endpoint to handle PDF uploads, text extraction, and metadata parsing.

    Args:
        file: Multipart uploaded file.

    Returns:
        PDFUploadResponse object containing extraction details.
    """
    filename = file.filename or "unknown.pdf"
    logger.info(f"Upload started for file: '{filename}'")

    # 1. Validate file
    try:
        content = await FileValidator.validate_pdf_upload(file)
    except FileValidationError as ve:
        error_msg = str(ve)
        logger.warning(f"Upload validation failed for '{filename}': {error_msg}")

        if "Only PDF files are allowed" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=error_msg,
            )
        elif "exceeds the maximum limit" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg,
            )
    except Exception as e:
        logger.error(f"Unexpected error during file upload validation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read upload stream: {str(e)}",
        )

    # 2. Extract text & save PDF
    try:
        response = pdf_service.process_pdf(content, filename)
        logger.info(f"Upload finished successfully for file: '{filename}' -> Assigned UUID file: '{response.file_name}'")
        return response
    except PaperProcessingError as pe:
        logger.error(f"Upload processing failed for '{filename}': {str(pe)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(pe),
        )
    except Exception as e:
        logger.error(f"Internal server error while processing '{filename}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the PDF file: {str(e)}",
        )
