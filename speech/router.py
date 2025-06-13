"""
Speech-to-text router for audio transcription services.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database.database import get_db
from auth.dependencies import get_current_user
from database.models import User
from speech.schemas import TranscriptionRequest, TranscriptionResponse
from speech.services import SpeechService

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = "en-US",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transcribe audio file to text using speech-to-text service.
    This endpoint acts as a proxy to external speech-to-text APIs
    and manages API keys securely on the backend.
    """
    speech_service = SpeechService()
    
    try:
        # Validate file type
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Transcribe audio
        transcript = await speech_service.transcribe_audio(
            audio_data=audio_data,
            content_type=audio_file.content_type,
            language=language
        )
        
        return TranscriptionResponse(
            transcript=transcript,
            language=language,
            confidence=0.95  # Placeholder confidence score
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Audio transcription failed")

@router.post("/transcribe-url")
async def transcribe_audio_url(
    request: TranscriptionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Transcribe audio from URL using speech-to-text service.
    """
    speech_service = SpeechService()
    
    try:
        transcript = await speech_service.transcribe_audio_url(
            audio_url=request.audio_url,
            language=request.language
        )
        
        return TranscriptionResponse(
            transcript=transcript,
            language=request.language,
            confidence=0.95
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Audio transcription failed")

@router.get("/supported-languages")
async def get_supported_languages(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of supported languages for speech-to-text.
    """
    return {
        "languages": [
            {"code": "en-US", "name": "English (US)"},
            {"code": "en-GB", "name": "English (UK)"},
            {"code": "es-ES", "name": "Spanish (Spain)"},
            {"code": "es-MX", "name": "Spanish (Mexico)"},
            {"code": "fr-FR", "name": "French (France)"},
            {"code": "de-DE", "name": "German (Germany)"},
            {"code": "it-IT", "name": "Italian (Italy)"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)"},
            {"code": "ja-JP", "name": "Japanese (Japan)"},
            {"code": "ko-KR", "name": "Korean (South Korea)"},
            {"code": "zh-CN", "name": "Chinese (Simplified)"},
            {"code": "hi-IN", "name": "Hindi (India)"}
        ]
    }

@router.get("/service-status")
async def get_service_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of speech-to-text service.
    """
    speech_service = SpeechService()
    status = await speech_service.check_service_status()
    
    return {
        "service": "Speech-to-Text",
        "status": status,
        "provider": "Azure Speech Services" if speech_service.has_azure_config() else "Not configured"
    }
