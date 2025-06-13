"""
Workflows router for workflow generation and management.
"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from auth.dependencies import get_current_user
from database.models import User, Workflow
from workflows.schemas import (
    WorkflowInput, 
    GeneratedWorkflow, 
    WorkflowCredentials, 
    WorkflowUpdate,
    WorkflowListResponse
)
from workflows.services import WorkflowService

router = APIRouter()

@router.post("/generate", response_model=GeneratedWorkflow)
async def generate_workflow(
    workflow_input: WorkflowInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate workflow code from natural language prompt.
    This is the core functionality of Cue - converting user descriptions into executable workflows.
    """
    workflow_service = WorkflowService(db)
    try:
        generated_workflow = await workflow_service.generate_workflow(
            user_id=current_user.id,
            prompt=workflow_input.prompt,
            input_type=workflow_input.input_type
        )
        return generated_workflow
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Workflow generation failed")

@router.post("/{workflow_id}/credentials", response_model=WorkflowUpdate)
async def update_workflow_credentials(
    workflow_id: int = Path(..., description="Workflow ID"),
    credentials: WorkflowCredentials = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update workflow with user-provided API credentials.
    Replaces placeholders in the generated code with actual credential values.
    """
    workflow_service = WorkflowService(db)
    try:
        updated_workflow = await workflow_service.update_workflow_credentials(
            workflow_id=workflow_id,
            user_id=current_user.id,
            credentials=credentials.credentials
        )
        return updated_workflow
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update workflow credentials")

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: int = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific workflow by ID.
    """
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "workflow_id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "original_prompt": workflow.original_prompt,
        "generated_code_skeleton": workflow.generated_code_skeleton,
        "final_code": workflow.final_code,
        "identified_tools": workflow.identified_tools,
        "nodes": workflow.nodes,
        "credentials_configured": workflow.credentials_configured,
        "validation_status": workflow.validation_status,
        "is_deployed": workflow.is_deployed,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at
    }

@router.get("/", response_model=List[WorkflowListResponse])
async def list_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all workflows for the current user.
    """
    workflows = db.query(Workflow).filter(
        Workflow.user_id == current_user.id
    ).order_by(Workflow.created_at.desc()).all()
    
    return [
        WorkflowListResponse(
            workflow_id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            validation_status=workflow.validation_status,
            credentials_configured=workflow.credentials_configured,
            is_deployed=workflow.is_deployed,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
        for workflow in workflows
    ]

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a workflow.
    """
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    
    return {"message": "Workflow deleted successfully"}
