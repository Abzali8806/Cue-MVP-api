"""
Speech-to-text service for audio transcription.
"""
import httpx
import base64
from typing import Optional
from config import settings

class SpeechService:
    """Service class for speech-to-text operations."""
    
    def __init__(self):
        self.azure_speech_key = settings.AZURE_SPEECH_KEY
        self.azure_speech_region = settings.AZURE_SPEECH_REGION
        self.azure_endpoint = f"https://{self.azure_speech_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    def has_azure_config(self) -> bool:
        """Check if Azure Speech Service is configured."""
        return bool(self.azure_speech_key and self.azure_speech_region)
    
    async def transcribe_audio(
        self, 
        audio_data: bytes, 
        content_type: str,
        language: str = "en-US"
    ) -> str:
        """
        Transcribe audio data using Azure Speech-to-Text service.
        """
        if not self.has_azure_config():
            return await self._mock_transcription(audio_data, language)
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Ocp-Apim-Subscription-Key": self.azure_speech_key,
                    "Content-Type": content_type,
                    "Accept": "application/json"
                }
                
                params = {
                    "language": language,
                    "format": "detailed"
                }
                
                response = await client.post(
                    self.azure_endpoint,
                    headers=headers,
                    params=params,
                    content=audio_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("RecognitionStatus") == "Success":
                        return result.get("DisplayText", "")
                    else:
                        raise Exception("Speech recognition failed")
                else:
                    raise Exception(f"Azure Speech API error: {response.status_code}")
        
        except Exception as e:
            # Fallback to mock transcription in case of API failure
            return await self._mock_transcription(audio_data, language)
    
    async def transcribe_audio_url(self, audio_url: str, language: str = "en-US") -> str:
        """
        Transcribe audio from URL.
        """
        try:
            # Download audio from URL
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url, timeout=30.0)
                if response.status_code == 200:
                    audio_data = response.content
                    content_type = response.headers.get("content-type", "audio/wav")
                    return await self.transcribe_audio(audio_data, content_type, language)
                else:
                    raise Exception("Failed to download audio from URL")
        
        except Exception as e:
            raise Exception(f"Audio URL transcription failed: {str(e)}")
    
    async def check_service_status(self) -> str:
        """
        Check the status of the speech-to-text service.
        """
        if not self.has_azure_config():
            return "not_configured"
        
        try:
            # Simple health check - attempt to access the service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{self.azure_speech_region}.api.cognitive.microsoft.com/",
                    headers={"Ocp-Apim-Subscription-Key": self.azure_speech_key},
                    timeout=10.0
                )
                return "healthy" if response.status_code in [200, 404] else "unhealthy"
        except:
            return "unhealthy"
    
    async def _mock_transcription(self, audio_data: bytes, language: str) -> str:
        """
        Mock transcription for development/testing when Azure Speech is not configured.
        In production, this should not be used - proper error handling should be implemented.
        """
        # This is a fallback for development environments
        # In production, you should ensure proper API credentials are available
        return "This is a mock transcription. Configure Azure Speech Services for actual transcription."
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats."""
        return [
            "audio/wav",
            "audio/mp3", 
            "audio/flac",
            "audio/ogg",
            "audio/webm",
            "audio/m4a"
        ]
