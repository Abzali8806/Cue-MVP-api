"""
Code validation router for validating generated Python code.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from auth.dependencies import get_current_user
from database.models import User
from validation.schemas import CodeValidationRequest, CodeValidationResponse
from validation.services import ValidationService

router = APIRouter()

@router.post("/validate", response_model=CodeValidationResponse)
async def validate_code(
    validation_request: CodeValidationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate Python code for syntax, modules, and production readiness.
    This endpoint performs comprehensive code validation including:
    - Syntax validation
    - Module currency checks (no deprecated modules)
    - Security analysis
    - Production readiness assessment
    """
    validation_service = ValidationService(db)
    
    try:
        validation_result = await validation_service.validate_code(
            code=validation_request.code_to_validate,
            validation_stage=validation_request.validation_stage,
            user_id=current_user.id
        )
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Code validation failed")

@router.post("/syntax-check")
async def quick_syntax_check(
    code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Quick syntax validation endpoint for real-time feedback.
    """
    validation_service = ValidationService(None)  # No DB needed for syntax check
    
    try:
        is_valid, errors = validation_service.check_syntax(code)
        return {
            "is_valid": is_valid,
            "syntax_errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Syntax check failed")

@router.get("/validation-rules")
async def get_validation_rules(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current validation rules and guidelines.
    """
    return {
        "syntax_rules": [
            "Valid Python syntax required",
            "No syntax errors allowed",
            "Proper indentation required"
        ],
        "module_rules": [
            "No deprecated modules",
            "Only standard library and approved third-party modules",
            "Security-conscious module usage"
        ],
        "security_rules": [
            "No hardcoded credentials",
            "Proper input sanitization",
            "No dangerous function usage (eval, exec, etc.)",
            "Safe file operations only"
        ],
        "production_rules": [
            "Proper error handling",
            "Logging implementation",
            "Environment variable usage for configuration",
            "No debugging code in production"
        ]
    }
