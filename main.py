"""
Main FastAPI application for Cue MVP Backend API Gateway.
This is a headless API service that integrates with the React frontend.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from config import settings
from database.database import engine, Base
from database.redis_client import redis_manager
from auth.router import router as auth_router
from workflows.router import router as workflows_router
from validation.router import router as validation_router
from speech.router import router as speech_router
from core.exceptions import CustomException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI(
    title="Cue MVP API Gateway",
    description="Backend API service for Cue workflow automation platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Configure CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom exception handler
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    try:
        # Initialize Redis connection
        redis_manager.connect()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    try:
        # Close Redis connection
        redis_manager.disconnect()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API service is running."""
    try:
        # Test database connection
        from database.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        # Test Redis connection
        from database.redis_client import get_redis
        redis_client = get_redis()
        redis_client.ping()
        
        return {
            "status": "ok",
            "database": "connected",
            "redis": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": str(e),
                "environment": settings.ENVIRONMENT
            }
        )

# Include routers for different modules
app.include_router(auth_router, tags=["Authentication"])
app.include_router(workflows_router, prefix="/workflows", tags=["Workflows"])
app.include_router(validation_router, prefix="/code", tags=["Code Validation"])
app.include_router(speech_router, prefix="/speech", tags=["Speech-to-Text"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Cue MVP API Gateway",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "Documentation disabled in production",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
