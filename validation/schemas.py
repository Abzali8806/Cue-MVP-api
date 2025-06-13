"""
Pydantic schemas for code validation data structures.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel

class CodeValidationRequest(BaseModel):
    """Request schema for code validation."""
    code_to_validate: str
    validation_stage: Literal["initial_skeleton", "final_with_credentials"]

class ValidationError(BaseModel):
    """Validation error schema."""
    line: int
    message: str
    severity: str = "error"  # "error", "warning", "info"

class ValidationSuggestion(BaseModel):
    """Validation suggestion schema."""
    type: str  # "improvement", "performance", "security", "critical"
    message: str
    example: Optional[str] = None

class CodeValidationResponse(BaseModel):
    """Response schema for code validation."""
    is_valid: bool
    validation_errors: List[ValidationError]
    suggestions: List[ValidationSuggestion]

class SyntaxCheckResponse(BaseModel):
    """Response schema for syntax check."""
    is_valid: bool
    syntax_errors: List[dict]
