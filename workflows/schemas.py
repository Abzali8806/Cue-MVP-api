"""
Pydantic schemas for workflow-related data structures.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel

class WorkflowInput(BaseModel):
    """Input schema for workflow generation."""
    prompt: str
    input_type: Literal["text", "speech_transcript"] = "text"

class ToolInfo(BaseModel):
    """Tool information schema."""
    name: str
    credentials_needed: List[str]

class WorkflowNode(BaseModel):
    """Workflow node for frontend visualization."""
    id: str
    type: str
    label: str
    position: Dict[str, int]

class GeneratedWorkflow(BaseModel):
    """Response schema for generated workflow."""
    workflow_id: int
    generated_code_skeleton: str
    identified_tools: List[ToolInfo]
    nodes: List[WorkflowNode]

class WorkflowCredentials(BaseModel):
    """Input schema for workflow credentials."""
    credentials: Dict[str, str]

class WorkflowUpdate(BaseModel):
    """Response schema for workflow update."""
    workflow_id: int
    updated_code: str

class WorkflowListResponse(BaseModel):
    """Response schema for workflow list."""
    workflow_id: int
    name: str
    description: Optional[str]
    validation_status: str
    credentials_configured: bool
    is_deployed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class WorkflowDetail(BaseModel):
    """Detailed workflow response schema."""
    workflow_id: int
    name: str
    description: Optional[str]
    original_prompt: str
    generated_code_skeleton: Optional[str]
    final_code: Optional[str]
    identified_tools: Optional[List[ToolInfo]]
    nodes: Optional[List[WorkflowNode]]
    credentials_configured: bool
    validation_status: str
    is_deployed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
