"""
Pydantic schemas for authentication-related data structures.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """JWT token payload data."""
    user_id: Optional[int] = None

class UserProfile(BaseModel):
    """User profile response schema."""
    id: int
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    profileImageUrl: Optional[str] = None
    displayName: Optional[str] = None
    provider: str
    providerId: str
    rememberMe: Optional[bool] = False
    
    # Onboarding fields
    companyName: Optional[str] = None
    industry: Optional[str] = None
    roleAtCompany: Optional[str] = None
    purposeUseCase: Optional[str] = None
    onboardingCompleted: Optional[bool] = False
    
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True

class OnboardingData(BaseModel):
    """Onboarding form data schema."""
    firstName: str
    lastName: str
    companyName: str
    industry: str
    roleAtCompany: str
    purposeUseCase: Optional[str] = None

class ProfileUpdateData(BaseModel):
    """Profile update data schema."""
    displayName: Optional[str] = None
    rememberMe: Optional[bool] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName: Optional[str] = None
    industry: Optional[str] = None
    roleAtCompany: Optional[str] = None
    purposeUseCase: Optional[str] = None

class GoogleUserInfo(BaseModel):
    """Google OAuth user information schema."""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: Optional[bool] = None

class GitHubUserInfo(BaseModel):
    """GitHub OAuth user information schema."""
    id: int
    login: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class OAuthCallback(BaseModel):
    """OAuth callback request schema."""
    code: str
    state: str
