"""
SQLAlchemy ORM models for the Cue MVP application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User model for storing user account information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    oauth_provider = Column(String(50), nullable=False)  # 'google' or 'github'
    oauth_id = Column(String(255), nullable=False)  # ID from OAuth provider
    profile_picture = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflows = relationship("Workflow", back_populates="user")
    oauth_tokens = relationship("OAuthToken", back_populates="user")

class OAuthToken(Base):
    """OAuth token storage for maintaining refresh tokens."""
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # 'google' or 'github'
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="oauth_tokens")

class Workflow(Base):
    """Workflow model for storing generated workflows."""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    original_prompt = Column(Text, nullable=False)
    input_type = Column(String(50), default="text")  # 'text' or 'speech_transcript'
    generated_code_skeleton = Column(Text, nullable=True)
    final_code = Column(Text, nullable=True)
    identified_tools = Column(JSON, nullable=True)  # Store tools as JSON
    nodes = Column(JSON, nullable=True)  # Store workflow nodes for frontend visualization
    credentials_configured = Column(Boolean, default=False)
    validation_status = Column(String(50), default="pending")  # 'pending', 'valid', 'invalid'
    validation_errors = Column(JSON, nullable=True)
    is_deployed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    credentials = relationship("WorkflowCredential", back_populates="workflow")

class WorkflowCredential(Base):
    """Workflow credentials for storing API keys and tokens."""
    __tablename__ = "workflow_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    tool_name = Column(String(255), nullable=False)
    credential_name = Column(String(255), nullable=False)  # e.g., 'API_KEY', 'TOKEN'
    credential_value = Column(Text, nullable=False)  # Encrypted in production
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="credentials")

class ValidationLog(Base):
    """Validation log for tracking code validation attempts."""
    __tablename__ = "validation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    code_snippet = Column(Text, nullable=False)
    validation_stage = Column(String(50), nullable=False)  # 'initial_skeleton' or 'final_with_credentials'
    is_valid = Column(Boolean, nullable=False)
    validation_errors = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
