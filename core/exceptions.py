"""
Custom exception handlers for the FastAPI application.
"""
from fastapi import HTTPException

class CustomException(HTTPException):
    """Base custom exception class."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class AuthenticationError(CustomException):
    """Authentication-related errors."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)

class AuthorizationError(CustomException):
    """Authorization-related errors."""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=403, detail=detail)

class NotFoundError(CustomException):
    """Resource not found errors."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class ValidationError(CustomException):
    """Validation-related errors."""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=400, detail=detail)

class WorkflowGenerationError(CustomException):
    """Workflow generation-related errors."""
    def __init__(self, detail: str = "Workflow generation failed"):
        super().__init__(status_code=500, detail=detail)

class CodeValidationError(CustomException):
    """Code validation-related errors."""
    def __init__(self, detail: str = "Code validation failed"):
        super().__init__(status_code=400, detail=detail)

class ExternalServiceError(CustomException):
    """External service integration errors."""
    def __init__(self, detail: str = "External service error", status_code: int = 502):
        super().__init__(status_code=status_code, detail=detail)
