"""
Authentication router for OAuth callbacks and user management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.database import get_db
from auth.schemas import Token, UserProfile
from auth.services import AuthService
from auth.dependencies import get_current_user
from database.models import User

router = APIRouter()

@router.get("/google/callback", response_model=Token)
async def google_oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback and return JWT token.
    """
    auth_service = AuthService(db)
    try:
        token = await auth_service.handle_google_callback(code, state)
        return token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="OAuth authentication failed")

@router.get("/github/callback", response_model=Token)
async def github_oauth_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """
    Handle GitHub OAuth callback and return JWT token.
    """
    auth_service = AuthService(db)
    try:
        token = await auth_service.handle_github_callback(code, state)
        return token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="OAuth authentication failed")

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
        name=current_user.name,
        oauth_provider=current_user.oauth_provider,
        profile_picture=current_user.profile_picture,
        is_active=current_user.is_active,
        created_at=current_user.created_at
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
