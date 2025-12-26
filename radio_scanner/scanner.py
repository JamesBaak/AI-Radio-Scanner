"""Radio scanner service that coordinates SDR, transcription, and recording."""
import logging
import os
from datetime import datetime
from typing import List, Tuple
from .sdr_controller import SDRController
from .transcription import TranscriptionService
from .config import Config

logger = logging.getLogger(__name__)


class RadioScanner:
    """Main radio scanner service."""
    
    def __init__(self, config: Config):
        """
        Initialize radio scanner.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.sdr = SDRController(
            sample_rate=config.SDR_SAMPLE_RATE,
            gain=config.SDR_GAIN
        )
        self.transcription = TranscriptionService()
        self.active_frequencies = []
    
    def initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Initializing Radio Scanner...")
        
        # Ensure directories exist
        Config.ensure_directories()
        
        # Initialize SDR
        if not self.sdr.initialize():
            logger.error("Failed to initialize SDR")
            return False
        
        # Initialize transcription service
        if not self.transcription.initialize():
            logger.error("Failed to initialize transcription service")
            return False
        
        logger.info("Radio Scanner initialized successfully")
        return True
    
    def scan_frequencies(self) -> List[Tuple[int, float, bool]]:
        """
        Scan all configured frequencies for activity.
        
        Returns:
            List of tuples (frequency, signal_strength, is_active)
        """
        logger.info("Starting frequency scan...")
        
        all_frequencies = self.config.AM_FREQUENCIES + self.config.FM_FREQUENCIES
        results = []
        
        for frequency in all_frequencies:
            is_active, signal_strength = self.sdr.detect_signal(
                frequency,
                threshold=self.config.SIGNAL_THRESHOLD,
                duration=self.config.DETECTION_DURATION
            )
            
            results.append((frequency, signal_strength, is_active))
            
            if is_active:
                self.active_frequencies.append(frequency)
        
        logger.info(f"Scan complete: {len(self.active_frequencies)} active frequencies found")
        return results
    
    def record_and_transcribe_frequency(self, frequency: int, duration: int = 60) -> Tuple[bool, str, str]:
        """
        Record and transcribe a frequency.
        
        Args:
            frequency: Frequency to record in Hz
            duration: Recording duration in seconds
            
        Returns:
            Tuple of (success, recording_file, transcript_file)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        freq_label = self._format_frequency_label(frequency)
        
        # Generate file paths
        recording_file = os.path.join(
            self.config.RECORDING_DIR,
            f"{timestamp}_{freq_label}.wav"
        )
        transcript_file = os.path.join(
            self.config.TRANSCRIPT_DIR,
            f"{timestamp}_{freq_label}.txt"
        )
        
        logger.info(f"Recording {duration}s from {freq_label}...")
        
        # Record audio
        if not self.sdr.record_frequency(frequency, duration, recording_file):
            logger.error(f"Failed to record {freq_label}")
            return False, "", ""
        
        # Transcribe audio
        logger.info(f"Transcribing recording from {freq_label}...")
        transcript = self.transcription.transcribe_audio(recording_file, transcript_file)
        
        if not transcript:
            logger.error(f"Failed to transcribe {freq_label}")
            return False, recording_file, ""
        
        logger.info(f"Successfully recorded and transcribed {freq_label}")
        return True, recording_file, transcript_file
    
    def process_active_frequencies(self, duration: int = 60) -> List[Tuple[int, str, str]]:
        """
        Record and transcribe all active frequencies.
        
        Args:
            duration: Recording duration in seconds per frequency
            
        Returns:
            List of tuples (frequency, recording_file, transcript_file)
        """
        results = []
        
        if not self.active_frequencies:
            logger.warning("No active frequencies to process")
            return results
        
        logger.info(f"Processing {len(self.active_frequencies)} active frequencies...")
        
        for frequency in self.active_frequencies:
            success, recording_file, transcript_file = self.record_and_transcribe_frequency(
                frequency, duration
            )
            
            if success:
                results.append((frequency, recording_file, transcript_file))
        
        # Clear active frequencies after processing
        self.active_frequencies = []
        
        logger.info(f"Processed {len(results)} frequencies successfully")
        return results
    
    def _format_frequency_label(self, frequency: int) -> str:
        """Format frequency as a filename-safe label."""
        if frequency < 30000000:  # AM
            return f"AM_{frequency // 1000}kHz"
        else:  # FM
            return f"FM_{frequency / 1000000:.1f}MHz".replace('.', '_')
    
    def close(self):
        """Clean up resources."""
        self.sdr.close()
        logger.info("Radio Scanner closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
