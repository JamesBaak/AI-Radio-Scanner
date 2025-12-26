"""Configuration management for the radio scanner."""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for radio scanner settings."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # SDR Configuration
    SDR_SAMPLE_RATE: int = int(os.getenv("SDR_SAMPLE_RATE", "2400000"))
    SDR_GAIN: str = os.getenv("SDR_GAIN", "auto")
    
    # Frequency Settings
    AM_FREQUENCIES: List[int] = [
        int(f) for f in os.getenv("AM_FREQUENCIES", "530000,1000000,1500000").split(",")
    ]
    FM_FREQUENCIES: List[int] = [
        int(f) for f in os.getenv("FM_FREQUENCIES", "88100000,95500000,101100000,107900000").split(",")
    ]
    
    # Detection Settings
    SIGNAL_THRESHOLD: float = float(os.getenv("SIGNAL_THRESHOLD", "-50.0"))
    DETECTION_DURATION: int = int(os.getenv("DETECTION_DURATION", "5"))
    
    # Recording Settings
    RECORDING_DIR: str = os.getenv("RECORDING_DIR", "./recordings")
    TRANSCRIPT_DIR: str = os.getenv("TRANSCRIPT_DIR", "./transcripts")
    SUMMARY_DIR: str = os.getenv("SUMMARY_DIR", "./summaries")
    
    # Summarization Schedule
    SUMMARY_SCHEDULE_HOUR: int = int(os.getenv("SUMMARY_SCHEDULE_HOUR", "1"))
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        os.makedirs(cls.RECORDING_DIR, exist_ok=True)
        os.makedirs(cls.TRANSCRIPT_DIR, exist_ok=True)
        os.makedirs(cls.SUMMARY_DIR, exist_ok=True)
