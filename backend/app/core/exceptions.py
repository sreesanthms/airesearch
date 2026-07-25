"""
Custom exception classes.
"""

class ResearchPilotException(Exception):
    """Base exception for ResearchPilot."""
    pass

class PaperNotFoundError(ResearchPilotException):
    """Raised when a paper is not found."""
    pass

class PaperProcessingError(ResearchPilotException):
    """Raised when there is an error processing a paper."""
    pass

class FileValidationError(ResearchPilotException):
    """Raised when file validation fails."""
    pass

class ExternalServiceError(ResearchPilotException):
    """Raised when an external service fails."""
    pass
