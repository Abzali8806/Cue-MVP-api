"""
Authentication service layer for OAuth and JWT operations.
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from config import settings
from database.models import User, OAuthToken
from auth.schemas import Token, GoogleUserInfo, GitHubUserInfo
from core.security import create_access_token

class AuthService:
    """Service class for handling authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def handle_google_callback(self, code: str, state: str) -> Token:
        """
        Handle Google OAuth callback and return JWT token.
        """
        # Exchange authorization code for access token
        token_data = await self._exchange_google_code(code)
        
        # Get user info from Google API
        user_info = await self._get_google_user_info(token_data["access_token"])
        
        # Create or get user
        user = self._get_or_create_user(
            email=user_info.email,
            name=user_info.name,
            oauth_provider="google",
            oauth_id=user_info.id,
            profile_picture=user_info.picture
        )
        
        # Store OAuth tokens
        self._store_oauth_token(
            user_id=user.id,
            provider="google",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in")
        )
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return Token(access_token=access_token, token_type="bearer")
    
    async def handle_github_callback(self, code: str, state: str) -> Token:
        """
        Handle GitHub OAuth callback and return JWT token.
        """
        # Exchange authorization code for access token
        token_data = await self._exchange_github_code(code)
        
        # Get user info from GitHub API
        user_info = await self._get_github_user_info(token_data["access_token"])
        
        # Create or get user
        user = self._get_or_create_user(
            email=user_info.email,
            name=user_info.name or user_info.login,
            oauth_provider="github",
            oauth_id=str(user_info.id),
            profile_picture=user_info.avatar_url
        )
        
        # Store OAuth tokens
        self._store_oauth_token(
            user_id=user.id,
            provider="github",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in")
        )
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return Token(access_token=access_token, token_type="bearer")
    
    async def _exchange_google_code(self, code: str) -> dict:
        """Exchange Google authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{settings.BACKEND_URL}/auth/google/callback"
                }
            )
            if response.status_code != 200:
                raise ValueError("Failed to exchange Google authorization code")
            return response.json()
    
    async def _exchange_github_code(self, code: str) -> dict:
        """Exchange GitHub authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": f"{settings.BACKEND_URL}/auth/github/callback"
                },
                headers={"Accept": "application/json"}
            )
            if response.status_code != 200:
                raise ValueError("Failed to exchange GitHub authorization code")
            return response.json()
    
    async def _get_google_user_info(self, access_token: str) -> GoogleUserInfo:
        """Get user information from Google API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code != 200:
                raise ValueError("Failed to get Google user info")
            return GoogleUserInfo(**response.json())
    
    async def _get_github_user_info(self, access_token: str) -> GitHubUserInfo:
        """Get user information from GitHub API."""
        async with httpx.AsyncClient() as client:
            # Get basic user info
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code != 200:
                raise ValueError("Failed to get GitHub user info")
            
            user_data = response.json()
            
            # Get user email if not public
            if not user_data.get("email"):
                email_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next((e for e in emails if e["primary"]), None)
                    if primary_email:
                        user_data["email"] = primary_email["email"]
            
            return GitHubUserInfo(**user_data)
    
    def _get_or_create_user(
        self,
        email: str,
        name: str,
        oauth_provider: str,
        oauth_id: str,
        profile_picture: Optional[str] = None
    ) -> User:
        """Get existing user or create new one."""
        # Try to find existing user by email
        user = self.db.query(User).filter(User.email == email).first()
        
        if user:
            # Update user info if needed
            if name:
                # Split name into first and last name
                name_parts = name.split(' ', 1)
                user.first_name = name_parts[0] if name_parts else None
                user.last_name = name_parts[1] if len(name_parts) > 1 else None
                user.display_name = name
            user.profile_picture = profile_picture
            user.updated_at = datetime.utcnow()
        else:
            # Split name into first and last name
            name_parts = name.split(' ', 1) if name else []
            first_name = name_parts[0] if name_parts else None
            last_name = name_parts[1] if len(name_parts) > 1 else None
            
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                display_name=name,
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                profile_picture=profile_picture
            )
            self.db.add(user)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def _store_oauth_token(
        self,
        user_id: int,
        provider: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None
    ):
        """Store or update OAuth token for user."""
        # Remove existing token for this provider
        self.db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == provider
        ).delete()
        
        # Calculate expiration time
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Create new token record
        oauth_token = OAuthToken(
            user_id=user_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        
        self.db.add(oauth_token)
        self.db.commit()
