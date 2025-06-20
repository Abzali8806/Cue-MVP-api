"""
Configuration management using Pydantic BaseSettings.
Environment variables are loaded from the system environment.
"""
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # Database settings - Local PostgreSQL for Docker Compose
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cue_user:cue_password@db:5432/cue_development")
    
    # Redis settings - Local Redis for Docker Compose
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # JWT settings - REPLACE WITH SECURE RANDOM KEYS
    # Generate strong random keys for production: python -c "import secrets; print(secrets.token_urlsafe(32))"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 1 # 3600 seconds = 1 hour
    
    # OAuth settings - CONFIGURE WITH YOUR OAUTH APP CREDENTIALS
    # Get from: Google Cloud Console > APIs & Services > Credentials
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID_HERE")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET_HERE")
    
    # Get from: GitHub > Settings > Developer settings > OAuth Apps
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "YOUR_GITHUB_CLIENT_ID_HERE")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "YOUR_GITHUB_CLIENT_SECRET_HERE")
    
    # Backend URL for OAuth redirects
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # CORS settings - UPDATE WITH YOUR FRONTEND DOMAINS
    # Add your production frontend URLs here
    ALLOWED_ORIGINS: List[str] = [
        "https://cue-tracker-abzali20.replit.app",  # Your current frontend
        "http://localhost:3000",  # Local development (direct run)
        "http://localhost:5001",  # Local development (docker-compose)
        "http://localhost:5000",  # Local API
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000"
        # Add additional production domains as needed
    ]
    
    # AWS settings - CONFIGURE WITH YOUR AWS CREDENTIALS
    # Get from: AWS IAM > Users > Security credentials
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "YOUR_AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "YOUR_AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")  # Change to your preferred region
    
    # Speech-to-text service settings - OPTIONAL: CONFIGURE FOR AZURE SPEECH SERVICES
    # Get from: Azure Portal > Cognitive Services > Speech Services
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "YOUR_AZURE_SPEECH_KEY_IF_NEEDED")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "YOUR_AZURE_REGION_IF_NEEDED")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables

# Create settings instance
settings = Settings()
