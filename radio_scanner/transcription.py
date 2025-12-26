"""Transcription service using OpenAI Whisper."""
import logging
import os
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio to text using Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize transcription service.
        
        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the Whisper model.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import whisper
            
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            self._initialized = True
            logger.info("Whisper model loaded successfully")
            return True
            
        except ImportError:
            logger.warning("Whisper not available, using mock transcription")
            self._initialized = True  # Allow mock mode
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {e}")
            return False
    
    def transcribe_audio(self, audio_file: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_file: Path to the audio file
            output_file: Optional path to save the transcript
            
        Returns:
            Transcribed text or None if failed
        """
        if not self._initialized:
            logger.error("Transcription service not initialized")
            return None
        
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None
        
        try:
            if self.model:
                # Use Whisper for transcription
                logger.info(f"Transcribing {audio_file}...")
                result = self.model.transcribe(audio_file)
                transcript = result["text"]
            else:
                # Mock transcription
                logger.warning(f"Using mock transcription for {audio_file}")
                transcript = f"[Mock Transcript] Audio from {os.path.basename(audio_file)} recorded at {datetime.now()}"
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                logger.info(f"Transcript saved to {output_file}")
            
            logger.info(f"Transcription complete: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            logger.error(f"Error transcribing {audio_file}: {e}")
            return None
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Clean up if needed
        pass
