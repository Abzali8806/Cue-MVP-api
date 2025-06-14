"""
Authentication router for OAuth callbacks and user management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database.database import get_db
from auth.schemas import Token, UserProfile
from auth.services import AuthService
from auth.dependencies import get_current_user
from database.models import User
from config import settings

router = APIRouter()

@router.get("/google/callback")
async def google_oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback and redirect to frontend with JWT token.
    """
    auth_service = AuthService(db)
    try:
        token = await auth_service.handle_google_callback(code, state)
        # Redirect to frontend with token as query parameter
        frontend_url = "https://cue-tracker-abzali20.replit.app"
        return RedirectResponse(url=f"{frontend_url}/auth/callback?token={token.access_token}")
    except ValueError as e:
        # Redirect to frontend with error
        frontend_url = "https://cue-tracker-abzali20.replit.app"
        return RedirectResponse(url=f"{frontend_url}/auth/callback?error={str(e)}")
    except Exception as e:
        # Redirect to frontend with generic error
        frontend_url = "https://cue-tracker-abzali20.replit.app"
        return RedirectResponse(url=f"{frontend_url}/auth/callback?error=oauth_failed")

@router.get("/github/callback")
async def github_oauth_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """
    Handle GitHub OAuth callback and redirect to frontend with JWT token.
    """
    auth_service = AuthService(db)
    try:
        token = await auth_service.handle_github_callback(code, state)
        # Redirect to frontend with token as query parameter
        frontend_url = "https://cue-tracker-abzali20.replit.app"
        return RedirectResponse(url=f"{frontend_url}/auth/callback?token={token.access_token}")
    except ValueError as e:
        # Redirect to frontend with error
        frontend_url = "https://cue-tracker-abzali20.replit.app"
        return RedirectResponse(url=f"{frontend_url}/auth/callback?error={str(e)}")
    except Exception as e:
        # Redirect to frontend with generic error
        frontend_url = "https://cue-tracker-abzali20.replit.app"
        return RedirectResponse(url=f"{frontend_url}/auth/callback?error=oauth_failed")

@router.get("/users/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user profile.
    Requires valid JWT token in Authorization header.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        profileImageUrl=current_user.profile_picture,
        displayName=current_user.display_name,
        provider=current_user.oauth_provider,
        providerId=current_user.oauth_id,
        rememberMe=current_user.remember_me,
        createdAt=current_user.created_at,
        updatedAt=current_user.updated_at
    )

# Add API prefix for frontend compatibility
@router.get("/api/auth/user", response_model=UserProfile)
async def get_current_user_api(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user profile (API endpoint for frontend).
    Requires valid JWT token in Authorization header.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        profileImageUrl=current_user.profile_picture,
        displayName=current_user.display_name,
        provider=current_user.oauth_provider,
        providerId=current_user.oauth_id,
        rememberMe=current_user.remember_me,
        createdAt=current_user.created_at,
        updatedAt=current_user.updated_at
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout endpoint (primarily for frontend state management).
    Since we're using stateless JWT, this is mainly for frontend cleanup.
    """
    return {"message": "Successfully logged out"}

# Add API prefix for frontend compatibility
@router.post("/api/auth/logout")
async def logout_api(
    current_user: User = Depends(get_current_user)
):
    """
    Logout endpoint (API endpoint for frontend).
    Since we're using stateless JWT, this is mainly for frontend cleanup.
    """
    return {"message": "Successfully logged out"}

@router.get("/validate-token")
async def validate_token(
    current_user: User = Depends(get_current_user)
):
    """
    Validate JWT token and return user info.
    Useful for frontend to check token validity.
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email
    }
