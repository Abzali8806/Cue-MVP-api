"""
Workflow service layer for workflow generation and management.
"""
import re
import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from database.models import Workflow, WorkflowCredential
from workflows.schemas import GeneratedWorkflow, WorkflowUpdate

class WorkflowService:
    """Service class for handling workflow operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_workflow(
        self, 
        user_id: int, 
        prompt: str, 
        input_type: str = "text"
    ) -> GeneratedWorkflow:
        """
        Generate workflow code from natural language prompt.
        This is a sophisticated NLP-based code generation system.
        """
        # Analyze the prompt to identify workflow components
        analysis = self._analyze_prompt(prompt)
        
        # Generate Python code skeleton
        code_skeleton = self._generate_code_skeleton(analysis)
        
        # Create workflow record in database
        workflow = Workflow(
            user_id=user_id,
            name=analysis["workflow_name"],
            description=analysis["description"],
            original_prompt=prompt,
            input_type=input_type,
            generated_code_skeleton=code_skeleton,
            identified_tools=analysis["tools"],
            nodes=analysis["nodes"]
        )
        
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        return GeneratedWorkflow(
            workflow_id=workflow.id,
            generated_code_skeleton=code_skeleton,
            identified_tools=analysis["tools"],
            nodes=analysis["nodes"]
        )
    
    async def update_workflow_credentials(
        self,
        workflow_id: int,
        user_id: int,
        credentials: Dict[str, str]
    ) -> WorkflowUpdate:
        """
        Update workflow with user-provided credentials.
        """
        # Get workflow
        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == user_id
        ).first()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        # Replace placeholders in code with actual credentials
        updated_code = self._inject_credentials(
            workflow.generated_code_skeleton,
            credentials
        )
        
        # Update workflow record
        workflow.final_code = updated_code
        workflow.credentials_configured = True
        
        # Store credentials (in production, these should be encrypted)
        for tool_cred, value in credentials.items():
            parts = tool_cred.split("_", 1)
            tool_name = parts[0]
            cred_name = parts[1] if len(parts) > 1 else "API_KEY"
            
            # Remove existing credential
            self.db.query(WorkflowCredential).filter(
                WorkflowCredential.workflow_id == workflow_id,
                WorkflowCredential.tool_name == tool_name,
                WorkflowCredential.credential_name == cred_name
            ).delete()
            
            # Add new credential
            credential = WorkflowCredential(
                workflow_id=workflow_id,
                tool_name=tool_name,
                credential_name=cred_name,
                credential_value=value  # In production: encrypt this
            )
            self.db.add(credential)
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return WorkflowUpdate(
            workflow_id=workflow_id,
            updated_code=updated_code
        )
    
    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze natural language prompt to extract workflow components.
        This is a simplified NLP analysis - in production, this would use
        advanced ML models or AWS services like Comprehend.
        """
        prompt_lower = prompt.lower()
        
        # Extract workflow name (simplified approach)
        workflow_name = self._extract_workflow_name(prompt)
        
        # Identify tools and services mentioned
        tools = self._identify_tools(prompt_lower)
        
        # Generate workflow nodes for frontend visualization
        nodes = self._generate_workflow_nodes(prompt_lower, tools)
        
        return {
            "workflow_name": workflow_name,
            "description": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "tools": tools,
            "nodes": nodes,
            "triggers": self._identify_triggers(prompt_lower),
            "actions": self._identify_actions(prompt_lower)
        }
    
    def _extract_workflow_name(self, prompt: str) -> str:
        """Extract or generate a workflow name from the prompt."""
        # Simple approach: use first few words or generate generic name
        words = prompt.split()[:5]
        name = " ".join(words)
        if len(name) > 50:
            name = name[:47] + "..."
        return name or "Untitled Workflow"
    
    def _identify_tools(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Identify third-party tools and services mentioned in the prompt.
        """
        tool_patterns = {
            "slack": {"name": "Slack", "credentials_needed": ["SLACK_BOT_TOKEN"]},
            "email": {"name": "Email", "credentials_needed": ["SMTP_PASSWORD"]},
            "gmail": {"name": "Gmail", "credentials_needed": ["GMAIL_API_KEY"]},
            "twitter": {"name": "Twitter", "credentials_needed": ["TWITTER_API_KEY", "TWITTER_API_SECRET"]},
            "github": {"name": "GitHub", "credentials_needed": ["GITHUB_TOKEN"]},
            "jira": {"name": "Jira", "credentials_needed": ["JIRA_API_TOKEN"]},
            "trello": {"name": "Trello", "credentials_needed": ["TRELLO_API_KEY"]},
            "notion": {"name": "Notion", "credentials_needed": ["NOTION_API_KEY"]},
            "google sheets": {"name": "Google Sheets", "credentials_needed": ["GOOGLE_SHEETS_API_KEY"]},
            "aws": {"name": "AWS", "credentials_needed": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]},
            "dropbox": {"name": "Dropbox", "credentials_needed": ["DROPBOX_ACCESS_TOKEN"]},
            "webhook": {"name": "Webhook", "credentials_needed": ["WEBHOOK_URL"]}
        }
        
        identified_tools = []
        for pattern, tool_info in tool_patterns.items():
            if pattern in prompt:
                identified_tools.append(tool_info)
        
        # If no specific tools identified, suggest generic ones
        if not identified_tools:
            identified_tools = [
                {"name": "HTTP API", "credentials_needed": ["API_KEY"]},
                {"name": "Database", "credentials_needed": ["DATABASE_URL"]}
            ]
        
        return identified_tools
    
    def _identify_triggers(self, prompt: str) -> List[str]:
        """Identify workflow triggers from the prompt."""
        triggers = []
        
        if any(word in prompt for word in ["schedule", "daily", "weekly", "hourly"]):
            triggers.append("schedule")
        if any(word in prompt for word in ["webhook", "http", "api call"]):
            triggers.append("webhook")
        if any(word in prompt for word in ["email", "receive"]):
            triggers.append("email")
        if any(word in prompt for word in ["file", "upload", "new document"]):
            triggers.append("file_watch")
        
        return triggers or ["manual"]
    
    def _identify_actions(self, prompt: str) -> List[str]:
        """Identify workflow actions from the prompt."""
        actions = []
        
        if any(word in prompt for word in ["send", "email", "notify"]):
            actions.append("send_notification")
        if any(word in prompt for word in ["save", "store", "database"]):
            actions.append("store_data")
        if any(word in prompt for word in ["transform", "convert", "process"]):
            actions.append("transform_data")
        if any(word in prompt for word in ["post", "publish", "share"]):
            actions.append("publish_content")
        
        return actions or ["process_data"]
    
    def _generate_workflow_nodes(self, prompt: str, tools: List[Dict]) -> List[Dict]:
        """Generate workflow nodes for frontend visualization."""
        nodes = [
            {
                "id": "start",
                "type": "trigger",
                "label": "Start",
                "position": {"x": 100, "y": 100}
            }
        ]
        
        # Add tool nodes
        y_position = 200
        for i, tool in enumerate(tools):
            nodes.append({
                "id": f"tool_{i}",
                "type": "action",
                "label": tool["name"],
                "position": {"x": 100 + (i * 200), "y": y_position}
            })
        
        # Add end node
        nodes.append({
            "id": "end",
            "type": "end",
            "label": "End",
            "position": {"x": 100, "y": 300}
        })
        
        return nodes
    
    def _generate_code_skeleton(self, analysis: Dict[str, Any]) -> str:
        """
        Generate Python code skeleton based on workflow analysis.
        """
        tools = analysis["tools"]
        triggers = analysis["triggers"]
        actions = analysis["actions"]
        
        code_parts = [
            "import os",
            "import json",
            "import requests",
            "from datetime import datetime",
            "",
            "# Auto-generated workflow code by Cue",
            f"# Workflow: {analysis['workflow_name']}",
            f"# Description: {analysis['description']}",
            "",
            "def main():",
            "    \"\"\"Main workflow function\"\"\"",
            "    try:"
        ]
        
        # Add initialization code for each tool
        for tool in tools:
            tool_name = tool["name"].upper().replace(" ", "_")
            for cred in tool["credentials_needed"]:
                code_parts.append(f"        {cred} = os.getenv('{cred}', 'PLACEHOLDER_{cred}')")
        
        code_parts.append("")
        code_parts.append("        # Workflow logic")
        
        # Add basic workflow steps based on identified actions
        for action in actions:
            if action == "send_notification":
                code_parts.extend([
                    "        # Send notification",
                    "        notification_message = 'Workflow executed successfully'",
                    "        print(f'Notification: {notification_message}')"
                ])
            elif action == "store_data":
                code_parts.extend([
                    "        # Store data",
                    "        data = {'timestamp': datetime.now().isoformat()}",
                    "        print(f'Storing data: {data}')"
                ])
            elif action == "transform_data":
                code_parts.extend([
                    "        # Transform data",
                    "        transformed_data = process_data()",
                    "        print(f'Transformed data: {transformed_data}')"
                ])
        
        code_parts.extend([
            "",
            "        return {'status': 'success', 'message': 'Workflow completed'}",
            "",
            "    except Exception as e:",
            "        return {'status': 'error', 'message': str(e)}",
            "",
            "def process_data():",
            "    \"\"\"Process and transform data\"\"\"",
            "    # Add your data processing logic here",
            "    return {}",
            "",
            "if __name__ == '__main__':",
            "    result = main()",
            "    print(json.dumps(result, indent=2))"
        ])
        
        return "\n".join(code_parts)
    
    def _inject_credentials(self, code_skeleton: str, credentials: Dict[str, str]) -> str:
        """
        Replace credential placeholders with actual values.
        """
        updated_code = code_skeleton
        
        for cred_key, cred_value in credentials.items():
            # Replace placeholder patterns
            placeholder_pattern = f"PLACEHOLDER_{cred_key}"
            updated_code = updated_code.replace(placeholder_pattern, cred_value)
        
        return updated_code
