"""
Code validation service for validating generated Python code.
"""
import ast
import re
import sys
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from database.models import ValidationLog
from validation.schemas import CodeValidationResponse, ValidationError, ValidationSuggestion

class ValidationService:
    """Service class for code validation operations."""
    
    def __init__(self, db: Optional[Session]):
        self.db = db
        
        # Deprecated modules to check for
        self.deprecated_modules = {
            "imp": "Use importlib instead",
            "optparse": "Use argparse instead", 
            "platform.dist": "Use platform.freedesktop_os_release instead",
            "distutils": "Use setuptools instead",
            "asyncore": "Use asyncio instead",
            "asynchat": "Use asyncio instead"
        }
        
        # Dangerous functions to avoid
        self.dangerous_functions = {
            "eval", "exec", "compile", "__import__",
            "open" # We'll check for unsafe file operations
        }
        
        # Approved third-party modules
        self.approved_modules = {
            "requests", "httpx", "pandas", "numpy", "json", "datetime",
            "os", "sys", "logging", "re", "urllib", "base64", "hashlib",
            "boto3", "sqlalchemy", "pydantic", "fastapi", "flask"
        }
    
    async def validate_code(
        self, 
        code: str, 
        validation_stage: str,
        user_id: Optional[int] = None,
        workflow_id: Optional[int] = None
    ) -> CodeValidationResponse:
        """
        Comprehensive code validation.
        """
        validation_errors = []
        suggestions = []
        is_valid = True
        
        # 1. Syntax validation
        syntax_valid, syntax_errors = self.check_syntax(code)
        if not syntax_valid:
            is_valid = False
            validation_errors.extend([
                ValidationError(line=error.get("line", 0), message=error.get("message", ""))
                for error in syntax_errors
            ])
        
        # 2. Module validation (only if syntax is valid)
        if syntax_valid:
            module_issues = self.check_modules(code)
            if module_issues:
                validation_errors.extend(module_issues)
                if any(issue.severity == "error" for issue in module_issues):
                    is_valid = False
        
        # 3. Security validation
        security_issues = self.check_security(code)
        if security_issues:
            validation_errors.extend(security_issues)
            if any(issue.severity == "error" for issue in security_issues):
                is_valid = False
        
        # 4. Production readiness (for final stage)
        if validation_stage == "final_with_credentials":
            production_issues = self.check_production_readiness(code)
            if production_issues:
                validation_errors.extend(production_issues)
        
        # 5. Generate suggestions
        suggestions = self.generate_suggestions(code, validation_errors)
        
        # 6. Log validation attempt
        if self.db and user_id:
            self._log_validation(
                workflow_id=workflow_id,
                code=code,
                validation_stage=validation_stage,
                is_valid=is_valid,
                errors=[error.dict() for error in validation_errors],
                suggestions=[suggestion.dict() for suggestion in suggestions]
            )
        
        return CodeValidationResponse(
            is_valid=is_valid,
            validation_errors=validation_errors,
            suggestions=suggestions
        )
    
    def check_syntax(self, code: str) -> Tuple[bool, List[Dict]]:
        """
        Check Python syntax validity.
        """
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            return False, [{
                "line": e.lineno or 0,
                "message": f"Syntax Error: {e.msg}",
                "type": "syntax"
            }]
        except Exception as e:
            return False, [{
                "line": 0,
                "message": f"Parse Error: {str(e)}",
                "type": "parse"
            }]
    
    def check_modules(self, code: str) -> List[ValidationError]:
        """
        Check for deprecated or problematic modules.
        """
        errors = []
        
        # Parse import statements
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        if module_name in self.deprecated_modules:
                            errors.append(ValidationError(
                                line=node.lineno,
                                message=f"Deprecated module '{module_name}': {self.deprecated_modules[module_name]}",
                                severity="warning"
                            ))
                
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    if module_name and module_name in self.deprecated_modules:
                        errors.append(ValidationError(
                            line=node.lineno,
                            message=f"Deprecated module '{module_name}': {self.deprecated_modules[module_name]}",
                            severity="warning"
                        ))
        except:
            pass  # If parsing fails, syntax validation will catch it
        
        return errors
    
    def check_security(self, code: str) -> List[ValidationError]:
        """
        Check for security issues in the code.
        """
        errors = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for hardcoded credentials (basic patterns)
            if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']{8,}["\']', line_stripped, re.IGNORECASE):
                errors.append(ValidationError(
                    line=i,
                    message="Potential hardcoded credential detected. Use environment variables instead.",
                    severity="error"
                ))
            
            # Check for dangerous functions
            for func in self.dangerous_functions:
                if func in line_stripped:
                    if func == "open":
                        # Allow safe file operations
                        if "open(" in line_stripped and ("r'" in line_stripped or 'r"' in line_stripped):
                            continue  # Read-only operations are safer
                    
                    errors.append(ValidationError(
                        line=i,
                        message=f"Potentially dangerous function '{func}' detected. Review for security implications.",
                        severity="warning"
                    ))
            
            # Check for SQL injection patterns
            if re.search(r'execute\s*\(\s*["\'].*%.*["\']', line_stripped, re.IGNORECASE):
                errors.append(ValidationError(
                    line=i,
                    message="Potential SQL injection vulnerability. Use parameterized queries.",
                    severity="error"
                ))
        
        return errors
    
    def check_production_readiness(self, code: str) -> List[ValidationError]:
        """
        Check if code is production-ready.
        """
        errors = []
        lines = code.split('\n')
        
        has_error_handling = "try:" in code and "except" in code
        has_logging = "logging" in code or "print" in code
        uses_env_vars = "os.getenv" in code or "os.environ" in code
        
        if not has_error_handling:
            errors.append(ValidationError(
                line=0,
                message="Missing error handling. Add try-except blocks for production code.",
                severity="warning"
            ))
        
        if not uses_env_vars:
            errors.append(ValidationError(
                line=0,
                message="Consider using environment variables for configuration.",
                severity="info"
            ))
        
        # Check for debugging code
        for i, line in enumerate(lines, 1):
            if "print(" in line and "debug" in line.lower():
                errors.append(ValidationError(
                    line=i,
                    message="Debug print statement detected. Remove for production.",
                    severity="warning"
                ))
        
        return errors
    
    def generate_suggestions(self, code: str, errors: List[ValidationError]) -> List[ValidationSuggestion]:
        """
        Generate improvement suggestions based on validation results.
        """
        suggestions = []
        
        if not any("import logging" in line for line in code.split('\n')):
            suggestions.append(ValidationSuggestion(
                type="improvement",
                message="Consider adding logging for better monitoring and debugging.",
                example="import logging\nlogging.basicConfig(level=logging.INFO)"
            ))
        
        if "requests" in code and "timeout" not in code:
            suggestions.append(ValidationSuggestion(
                type="performance",
                message="Add timeout parameters to HTTP requests for better reliability.",
                example="response = requests.get(url, timeout=30)"
            ))
        
        if any(error.severity == "error" for error in errors):
            suggestions.append(ValidationSuggestion(
                type="critical",
                message="Fix all error-level issues before deploying to production.",
                example=""
            ))
        
        return suggestions
    
    def _log_validation(
        self,
        workflow_id: Optional[int],
        code: str,
        validation_stage: str,
        is_valid: bool,
        errors: List[Dict],
        suggestions: List[Dict]
    ):
        """
        Log validation attempt to database.
        """
        if not self.db:
            return
        
        validation_log = ValidationLog(
            workflow_id=workflow_id,
            code_snippet=code[:1000],  # Store first 1000 chars
            validation_stage=validation_stage,
            is_valid=is_valid,
            validation_errors=errors,
            suggestions=suggestions
        )
        
        self.db.add(validation_log)
        self.db.commit()
