"""
Pydantic schemas for speech-to-text data structures.
"""
from typing import Optional
from pydantic import BaseModel, HttpUrl

class TranscriptionRequest(BaseModel):
    """Request schema for audio transcription from URL."""
    audio_url: HttpUrl
    language: str = "en-US"

class TranscriptionResponse(BaseModel):
    """Response schema for audio transcription."""
    transcript: str
    language: str
    confidence: Optional[float] = None

class LanguageInfo(BaseModel):
    """Language information schema."""
    code: str
    name: str

class SupportedLanguagesResponse(BaseModel):
    """Response schema for supported languages."""
    languages: list[LanguageInfo]

class ServiceStatusResponse(BaseModel):
    """Response schema for service status."""
    service: str
    status: str
    provider: str
